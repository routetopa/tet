#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import nltk, re, pprint
from nltk import word_tokenize
import pyPdf
from pyPdf import PdfFileReader
import string
import RAKE.RAKE as rake
import operator
import ckanapi
import re

import os

try: 
  from urllib2 import urlopen
  from urllib2 import Request
  from urlparse import scheme_chars
  unicode = unicode
except ImportError: 
  from urllib.request import urlopen

import json
from .helpers import dataset_to_metadata_text, dataset_to_spod, name_to_url, resource_fields_to_text
from io import BytesIO
from dateutil.parser import parse

from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.html import strip_tags
from django.views import generic
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph
from django.shortcuts import render, redirect
import collections
import operator
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
from StringIO import StringIO
from collections import Counter
from django.utils.translation import ugettext as _
from django.utils.translation import activate
from django.utils import translation

styles = getSampleStyleSheet()
style_normal = styles['Normal']
style_heading1 = styles['Heading1']

def get_keywords(raw_text, stopwords_file):
    punctuation_exclude = set(string.punctuation)
    raw_text = ''.join(ch for ch in raw_text if ch not in punctuation_exclude)
    tokens = nltk.word_tokenize(raw_text)
    rake_object = rake.Rake(stopwords_file)
    text = '\t'.join(tokens)
    return rake_object.run(text)

def get_keywords_from_pdf(url, stopwords_file):
    remote_file = urlopen(Request(url)).read()
    memory_file = StringIO(remote_file)
    pdf_to_read = PdfFileReader(memory_file)
    keywords = False
    tokens = False
    keywords =[]
    for pageNum in xrange(pdf_to_read.getNumPages()):
        raw_text = pdf_to_read.getPage(pageNum).extractText()
        raked = get_keywords(raw_text,stopwords_file)
        keywords.extend(raked)
    return keywords

def index(request):

    template_name = 'browser/index.html'
    try:

        url_datasets = settings.CKAN_URL + "/api/3/stats/dataset_count"
        url_organizations = settings.CKAN_URL + "/api/3/stats/organization_count"

        res_datasets = urlopen(url_datasets)
        datasets_count_json = json.loads(res_datasets.read().decode('utf-8'))
        datasets_count = int(datasets_count_json['dataset_count'])

        res_organizations = urlopen(url_organizations)
        organizations_count_json = json.loads(res_organizations.read().decode('utf-8'))
        organizations_count = int(organizations_count_json['organization_count'])

    except Exception, e:
        datasets_count = 0
        organizations_count = 0
        pass

    context = {
        'datasets_count': datasets_count,
        'organizations_count': organizations_count,
        'CKAN_URL': settings.CKAN_URL,
    }

    return render(request, template_name, context)

def typeahead(request):
    try:
        results = {
          "success": True,
          "options": []
        }
        url = settings.CKAN_URL + "/api/3/util/tet/getconfig"
        res = urlopen(url)
        data = json.loads(res.read())
        for role in data["roles"]:
            results["options"].append("I am " + role)
        for cat in data["categories"]:
            results["options"].append("Interested in " + cat)
        return JsonResponse(results)
    except Exception, e:
        return JsonResponse({'success': False})

def table_api(request, resource_id, field_id):
    try:
        url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=99999"
        res = urlopen(url)
        data = json.loads(res.read())
        temp_data = json_normalize(data["result"]["records"])
        fields = data["result"]["fields"] # type_unified TODO
        record_count = 0
        results = {
          "success": True,
          "result" : {
            "resource_id": resource_id,
            "records" : [],
            "fields" : [
              {"id":"Name", "type" : "text"},
              {"id":"Range", "type" : "text"},
              {"id":"Frequency", "type" : "numeric"}
            ],
            "total" : 0,
            "limit":99999,
          }
        }
        for f in fields:
            if f["id"] == field_id:
                break
        if f["type"] ==  "numeric":
            c = f["id"]
            temp_data[c] = pd.to_numeric(temp_data[c], errors='coerce')
            dist = np.histogram(temp_data[c],11)
            for i in range (0, 11):
                record = {
                  "Name" : c,
                  "Range" : str(round(dist[1][i]))+" to "+str(round(dist[1][i+1])),
                  "Frequency" : int(dist[0][i])
                }
                results["result"]["records"].append(record)
                record_count += 1
        if f["type"] ==  "text":
            c = f["id"]
            counts = Counter(temp_data[c])
            for item in counts.most_common(10):
              value = item[0]
              if len(value) > 35:
                value = value[:35] + "..."
              record = {
                  "Name" : c,
                  "Value" : value,
                  "Count" : item[1]
              }
              results["result"]["records"].append(record)
              record_count += 1                 

        results["result"]["total"] = record_count
        response =  JsonResponse(results)
        response["Access-Control-Allow-Origin"] = "*"
        

        return response
    except Exception:
        raise Exception
        return JsonResponse({'success': False})

# TODO url param parsing
# TODO pagination
def search(request, query=False):

    template_name = 'browser/search.html'

    # display logic
    query = request.GET.get('query') or ''

    if query.lower().startswith(_("i am")):
        query =  "role::" + _(query.lower().replace(_("i am"), ""))
    if query.lower().startswith(_("interested in")):
        query =  "category::" + _(query.lower().replace(_("interested in"), ""))
    
    search_results = []
    filters = {}
    has_results = False

    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )

    api_result = ckan_api_instance.action.package_search(
        q=query,
        sort='relevance asc, metadata_modified desc',
        rows=1000,
        start=0,
    )

    if api_result["count"] > 0:
        has_results = True
        # prepare search results and the filters
        pattern = re.compile(query, re.IGNORECASE)

        themes = {}
        periods = {}
        locations = {}
        formats = {}

        locations_list = settings.LOCATIONS_LIST

        for idx, dataset in enumerate(api_result["results"]):
            # bold the query phrase
            if ( query ):
                dataset["title"] = pattern.sub("<strong>"+query+"</strong>", strip_tags(dataset["title"]))
                dataset["notes"] = pattern.sub("<strong>"+query+"</strong>", strip_tags(dataset["notes"]))

            # used in search / filtering JS
            dataset["relevance_key"] = idx
            dataset["name_key"] = strip_tags(dataset["title"])[:10].upper()
            dataset["date_key"] = parse(dataset["metadata_created"]).strftime("%Y%m%d%H%M%S")

            text = (dataset["title"] + dataset["notes"]).lower()

            if "category" in dataset.keys():
                categories = dataset["category"].split(",")
                dataset["category_key"] = " ".join(categories)
                for category in categories:
                    if category not in themes.keys():
                        themes[category] = 1
                    else:
                        themes[category] += 1

            dataset["year_key"] = ""
            for year in range(1900, 2020):
                syear = str(year)
                if text.find(syear) > 0:
                    dataset["year_key"] += " " + syear
                    if syear not in periods.keys():
                        periods[syear] = 1
                    else:
                        periods[syear] += 1

            dataset["location_key"] = ""
            for location in locations_list:
                slocation = location.lower() 
                if text.find(slocation) > 0:
                    dataset["location_key"] += slocation + " "
                    if location not in locations.keys():
                        locations[location] = 1
                    else:
                        locations[location] += 1

            dataset["format_key"] = ""
            if "resources" in dataset.keys():
                already_added = []
                for resource in dataset["resources"]:
                    dataset["format_key"] += resource["format"].lower() + " "

                    if resource["format"].lower() in already_added:
                        continue

                    if resource["format"].lower() in ["csv","xls"]:
                        dataset["has_table"] = True

                    if resource["format"].lower()  == "pdf":
                        dataset["has_pdf"] = True

                    if resource["format"] not in formats:
                        formats[resource["format"]] = 1
                    else:
                        formats[resource["format"]] += 1
                    already_added.append(resource["format"].lower())

            search_results.append(dataset)

        if "" in themes.keys():
            del themes[""]
        if "" in formats.keys():
            del formats[""]



        filters["themes"] = collections.OrderedDict(reversed(sorted(themes.items(), key=lambda x: int(x[1]))))
        filters["locations"] = collections.OrderedDict(reversed(sorted(locations.items(), key=lambda x: int(x[1]))))
        filters["periods"] = collections.OrderedDict(sorted(periods.items(), reverse=True))
        filters["formats"] = collections.OrderedDict(reversed(sorted(formats.items(), key=lambda x: int(x[1]))))



    context = {
        'query': query,
        'has_results': has_results,
        'search_results': search_results,
        'filters': filters,
        'CKAN_URL': settings.CKAN_URL,
    }

    return render(request, template_name, context)


def dataset(request, dataset_id):

    template_name = 'browser/dataset.html'

    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )
    resource_id = None 
    resource_fields = None
    related_datasets = None
    fields = None
    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
        try:
            url = settings.CKAN_URL + "/api/3/util/tet/get_recommended_datasets?pkg=" + dataset_id
            res = urlopen(url)
            related_datasets = json.loads(res.read())["datasets"]
        except Exception:
            pass
        if "resources" in dataset.keys():
            for resource in dataset["resources"]:
                if resource["format"].lower() in ["csv","xls"]:
                    dataset["has_table"] = True

                if resource["format"].lower()  == "pdf":
                    dataset["has_pdf"] = True
                if resource["format"].lower() in ["csv","xls"]:
                    try:
                        resource_id = resource["id"]
                        url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=5"
                        res = urlopen(url)
                        data = json.loads(res.read())
                        resource_fields = []
                        filter_list = ["long", "lat", "no.", "phone", "date","id", "code"] 
                        for field in data["result"]["fields"]:
                            name = field["id"]
                            found = False 
                            for f in filter_list:
                                if f in name.lower():
                                    found = True 
                            if found:
                                continue
                            if field["type"] == "numeric":
                                resource_fields.append((name, True))
                            elif field["type"] == "text":
                                resource_fields.append((name, False))
                            else:
                                pass
                        fields = data["result"]["fields"]
                        break
                    except Exception as e:
                        # print(str(e))
                        resource_id = None
                        resource_fields = None 
                        # raise Exception
    except Exception:
        raise Exception
    if resource_id and len(resource_fields) < 1:
        resource_id = None
    context = {
        'dataset_id': dataset_id,
        'dataset': dataset,
        'metadata_box': dataset_to_metadata_text(dataset),
        'spod_box_datasets': dataset_to_spod(dataset),
        'SPOD_URL': settings.SPOD_URL,
        'resource_fields': resource_fields,
        'related_datasets' : related_datasets,
        'CKAN_URL': settings.CKAN_URL + "/dataset/" + dataset_id + "?r=" + request.get_full_path(),
        'fields' : resource_fields_to_text(fields)
    }

    if resource_id:
        context['resource_id'] = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=9999",
        context['freq_resource_id'] = "/en/api/table/" + resource_id
    return render(request, template_name, context)


def dataset_as_app(request, dataset_id):
    return HttpResponse(dataset_id + ' as_app')


def dataset_as_table(request, dataset_id):
    template_name = 'browser/tabular.html'
    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )
    url = settings.CKAN_URL + "/dataset/" + dataset_id
    url_table = None
    url_pivottable = None
    resource_id = None
    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
        if "resources" in dataset.keys():
            for resource in dataset["resources"]:
                if resource["format"].lower() in ["csv","xls"]:
                    views = ckan_api_instance.action.resource_view_list(id=resource["id"])
                    resource_id = resource["id"]
                    for view in views:
                        if (view["view_type"]=="recline_view"):
                            url_table = settings.CKAN_URL + "/dataset/" + dataset_id + "/resource/" + resource["id"] + "/view/" + view["id"]
                            break
                    for view in views:
                        if (view["view_type"]=="pivottable"):
                            url_pivottable = settings.CKAN_URL + "/dataset/" + dataset_id + "/resource/" + resource["id"] + "/view/" + view["id"]
                            break
                    break
    except Exception:
        raise Exception

    context = {
        "url_table": url_table,
        'url_pivottable': url_pivottable,
        'dataset_id': dataset_id,
        'dataset': dataset,
        'metadata_box': dataset_to_metadata_text(dataset),
        'spod_box_datasets': dataset_to_spod(dataset),
        'SPOD_URL': settings.SPOD_URL,
        'CKAN_URL': settings.CKAN_URL + "/dataset/" + dataset_id + "?r=" + request.get_full_path(),
        'API_LINK' : settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=99999" 
     }

    return render(request, template_name, context)

# TODO summary: keywords, charts, extracted media
def dataset_as_pdf(request, dataset_id):

    template_name = 'browser/pdf.html'
    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )

    keywords = []
    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
        if "resources" in dataset.keys():
            for resource in dataset["resources"]:
                if resource["format"].lower() == "pdf":
                    context = {
                       "url" : resource["url"],
                       'CKAN_URL': settings.CKAN_URL + "/dataset/" + dataset_id + "?r=" + request.get_full_path()
                    }
                    path = (os.path.dirname(os.path.realpath(__file__)))
                    keywords = get_keywords_from_pdf(resource["url"],path+'/SmartStoplist.txt')
    except Exception:
        pass

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dataset_summary_by_tet.pdf"'

    buffer = BytesIO()

    doc = BaseDocTemplate(buffer, pagesize=letter)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='test', frames=frame)
    doc.addPageTemplates([template])
    text = []
    text.append(Paragraph(dataset["title"], style_heading1))
    text.append(Paragraph(dataset["notes"], style_normal))
    text.append(Paragraph(" ", style_normal))
    path = (os.path.dirname(os.path.realpath(__file__)))
    keywords.extend(get_keywords(dataset["notes"],path+'/SmartStoplist.txt'))
    text.append(Paragraph(" ", style_normal))
    text.append(Paragraph("Keywords", style_heading1))
    keyword_string = ""
    for k in keywords:
        keyword_string += k[0] + " (" + str(int(k[1])) + ") "
    text.append(Paragraph(keyword_string, style_normal))
    doc.build(text)
    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
