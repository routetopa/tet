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
import datetime
import dateutil
import os
import pickle 
try: 
  from urllib2 import urlopen
  from urllib2 import Request
  from urlparse import scheme_chars
  unicode = unicode
except ImportError: 
  from urllib.request import urlopen
import urllib
import json
from .helpers import dataset_to_metadata_text, dataset_to_spod, name_to_url, resource_fields_to_text
from io import BytesIO
from dateutil.parser import parse

from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse, StreamingHttpResponse
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
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from collections import Counter
from django.utils.translation import ugettext as _
from django.utils.translation import activate
from django.utils import translation
from watson_developer_cloud import AlchemyLanguageV1
from django.core.cache import cache
import shelve
import logging
from threading import Lock
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from django.contrib import messages
import sqlite3

mutex = Lock()
logger = logging.getLogger(__name__)
styles = getSampleStyleSheet()
style_normal = styles['Normal']
style_heading1 = styles['Heading1']
error_template = "browser/error.html"

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

    organizations = []
    tags = []
    roles = []
    categories = []

    try:
        # TODO ckan_api_instance
        url_datasets_count = settings.CKAN_URL + "/api/3/stats/dataset_count"
        url_organizations_count = settings.CKAN_URL + "/api/3/stats/organization_count"

        res_datasets_count = urlopen(url_datasets_count)
        datasets_count_json = json.loads(res_datasets_count.read().decode('utf-8'))
        datasets_count = int(datasets_count_json['dataset_count'])

        res_organizations_count = urlopen(url_organizations_count)
        organizations_count_json = json.loads(res_organizations_count.read().decode('utf-8'))
        organizations_count = int(organizations_count_json['organization_count'])

    except Exception as e:
        datasets_count = 0
        organizations_count = 0
        pass

    if not ( settings.TET_SIMPLE_HOMEPAGE ):
        # try:

            # organizations
            # TODO order by package_count
            url_organizations = settings.CKAN_URL + '/api/action/organization_list?all_fields=true&facet.field=["organization"]&facet.limit=10&rows=0&order_by=package_count'
            res_organizations = urlopen(url_organizations)
            res_organizations_json = json.loads(res_organizations.read().decode('utf-8'))

            if (res_organizations_json['success'] == True):
                organizations = res_organizations_json['result']

            # tags
            # TODO order by package_count
            url_tags = settings.CKAN_URL + '/api/action/package_search?facet.field=["tags"]&facet.limit=10&rows=0'
            res_tags = urlopen(url_tags)
            res_tags_json = json.loads(res_tags.read().decode('utf-8'))
            if (res_tags_json['success'] == True):
                tags = res_tags_json['result']['facets']['tags']

            try:
                # roles and categories
                # TODO Requires TET extension - note
                url_tet_rc = settings.CKAN_URL + "/api/3/util/tet/getconfig"
                tet_rc_res = urlopen(url_tet_rc)
                tet_rc_res_json = json.loads(tet_rc_res.read())
                for role in tet_rc_res_json["roles"]:
                    roles.append(role)
                for category in tet_rc_res_json["categories"]:
                    categories.append(category)

            # TODO HttpError handling
            # TODO load default values from JSON / config
            except Exception as e:
                pass

    context = {
        'datasets_count': datasets_count,
        'organizations_count': organizations_count,
        'TET_SIMPLE_HOMEPAGE': settings.TET_SIMPLE_HOMEPAGE,
        'HIDE_SEARCH_NAV': True,
        'organizations': organizations,
        'tags': tags,
        'roles': roles,
        'categories': categories
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
    except Exception as e:
        return JsonResponse({'success': False})

def cards(request):
    try:
        results = {
          "success": True,
          "cards": []
        }
        try:
            for indicator in settings.INDICATORS:
                try:
                    url = settings.CKAN_URL + "/api/action/datastore_search_sql?sql=" + urllib.quote(indicator["query"])
                    res = urlopen(url)
                    data = json.loads(res.read().decode('utf-8'))
                    for kw in data["result"]["records"]:
                        kw["title"] = indicator["title"]
                        results["cards"].append(kw)
                except Exception:
                    pass
        except Exception as e:
            pass
        return JsonResponse(results)
    except Exception as e:
        return JsonResponse({'success': False, "message" : str(e)})

def table_api(request, resource_id, field_id):
    url = settings.CKAN_URL +  "/api/action/datastore_search_sql?sql=" + urllib.quote("SELECT \"" + field_id + "\" FROM \"" + resource_id + "\"")
    return column_summary(url, field_id)

def query_api(request, query, field_id):
    url = settings.CKAN_URL + "/api/action/datastore_search_sql?sql=" + urllib.quote(query)
    return column_summary(url, field_id)

def column_summary(url, field_id):
    try:
        res = urlopen(url)
        data = json.loads(res.read().decode('utf-8'))
        temp_data = json_normalize(data["result"]["records"])
        fields = data["result"]["fields"] # type_unified TODO
        record_count = 0
        results = {
          "help": "http://google.com",
          "success": True,
          "result" : {
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
            results["result"]["fields"] = [ {"id":"Name", "type" : "text"},
              {"id":"Value", "type" : "text"},
              {"id":"count", "type" : "numeric"}
            ]               

        results["result"]["total"] = record_count
        response =  JsonResponse(results)
        response["Access-Control-Allow-Origin"] = "*"

        return response
    except Exception as e:
        return JsonResponse({'success': False})

def text_api(request, dataset_id, info_type):
    try:
        rich_text = cache_db(dataset_id)
        if len(rich_text) == 0:
            ckan_api_instance = ckanapi.RemoteCKAN(
                settings.CKAN_URL,
                user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
            )
            dataset = ckan_api_instance.action.package_show(
                id=dataset_id
            )
            if "resources" in dataset.keys():
                for resource in dataset["resources"]:
                    if resource["format"].lower() == "pdf":
                            rich_text = text_analytics(dataset_id, resource["url"], dataset["notes"])
        record_count = 0
        results = {
          "success": True,
          "result" : {
            "resource_id": dataset_id,
            "records" : [],
            "fields" : [
              {"id":"Name", "type" : "text"},
              {"id":"Relevance", "type" : "numeric"}
            ],
            "total" : 0,
            "limit":99999,
          }
        }

        if info_type == "summary":
            results["result"]["fields"][0] = "Summary"

        for item in rich_text[info_type]:
            if info_type == "summary":
                name = item
                record = {
                      "Summary" : name,
                      "Relevance" : 1
                }
            else:
                name = item["text"]
                if len(name) > 35:
                    name = name[:35] + "..."
                rel = float(item["relevance"])
                record = {
                      "Name" : name,
                      "Relevance" : rel
                }
            results["result"]["records"].append(record)
            record_count += 1

        results["result"]["total"] = record_count
        response =  JsonResponse(results)
        response["Access-Control-Allow-Origin"] = "*"
        
        return response
    except Exception as e:
        return JsonResponse({'success': False})

# TODO url param parsing
# TODO pagination
def search(request, query=False):

    template_name = 'browser/search.html'

    # display logic
    query           = request.GET.get('query') or ''
    fq              = request.GET.get('fq') or ''

    # homepage filters
    organization    = request.GET.get('organization') or ''
    tags            = request.GET.get('tags') or ''
    role            = request.GET.get('role') or ''
    category        = request.GET.get('category') or ''
    openness_score  = request.GET.get('openness_score') or ''

    HIDE_SEARCH_NAV = False

    # TODO rewrite + translation
    if query.lower().startswith(_("i am")):
        query =  "role::" + _(query.lower().replace(_("i am"), ""))
    if query.lower().startswith(_("interested in")):
        query =  "category::" + _(query.lower().replace(_("interested in"), ""))

    # facets
    if tags:
        fq += "tags:" + tags
    if organization:
        if fq:
            fq += "+"
        fq += "organization:" + organization
    if openness_score:
        if fq:
            fq += "+"
        fq += "openness_score:" + openness_score

    # TODO fix role & category
    if role:
        query = "role::" + role
    if category:
        query = "category::" + category

    search_results = []
    filters = {}
    has_results = False

    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )

    api_result = ckan_api_instance.action.package_search(
        q=query,
        fq=fq,
        sort='relevance asc, metadata_modified desc',
        rows=1000,
        start=0,
    )

    if api_result["count"] > 0:
        has_results = True
        # prepare search results and the filters
        pattern = re.compile(query, re.IGNORECASE)

        themes = {}
        tags = {}
        periods = {}
        locations = {}
        formats = {}

        locations_list = settings.LOCATIONS_LIST

        for idx, dataset in enumerate(api_result["results"]):
            # bold the query phrase
            if ( query ):
                dataset["title"] = pattern.sub("<mark>"+query+"</mark>", strip_tags(dataset["title"]))
                dataset["notes"] = pattern.sub("<mark>"+query+"</mark>", strip_tags(dataset["notes"]))

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

            dataset["tag_key"] = ""
            for tag in dataset["tags"]:
                if tag["name"].lower() not in tags.keys():
                    tags[tag["name"].lower()] = 1
                else:
                    tags[tag["name"].lower()] += 1

                dataset["tag_key"] += " " + tag["name"].lower()

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

                    if resource["format"].lower() == "pdf":
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
        filters["tags"] = collections.OrderedDict(reversed(sorted(tags.items(), key=lambda x: int(x[1]))))
        filters["locations"] = collections.OrderedDict(reversed(sorted(locations.items(), key=lambda x: int(x[1]))))
        filters["periods"] = collections.OrderedDict(sorted(periods.items(), reverse=True))
        filters["formats"] = collections.OrderedDict(reversed(sorted(formats.items(), key=lambda x: int(x[1]))))
    else:
        HIDE_SEARCH_NAV = True


    context = {
        'query': query,
        'has_results': has_results,
        'search_results': search_results,
        'filters': filters,
        'HIDE_SEARCH_NAV': HIDE_SEARCH_NAV,
    }

    return render(request, template_name, context)

def grading(number):
    if number < 35:
        return _("Very Poor")
    if number < 55:
        return _("Poor")
    elif number < 75:
        return _("Fair")
    elif number < 95:
        return _("Good")
    else:
        return _("Very good")


def compute_completeness(stats):
    print(stats)
    if stats is {}:
        return None 

    internal_attributes =["relationships_as_object","private","num_tags","id","metadata_created","metadata_modified","state",\
    "creator_user_id","type","resources","num_resources","tags","groups","relationships_as_subject","organization","name","isopen",\
    "url","notes","owner_org","extras","license_url","title","revision_id"]
    metadata_fields = [key for key in stats["ds"] if key not in internal_attributes]
    metadata_string = ""
    for f in metadata_fields:
        if stats["ds"][f] != "Not supplied":
            metadata_string += str(stats["ds"][f]) 
    description_length = len(stats["ds"]["notes"])
    stats["metadata"] = len(metadata_string)/50.0 * 100 if len(metadata_string) <= 50  else 100

    stats["description"] = description_length/600.0 * 100 if description_length <= 600 else 100
    if "fields" in stats:
        stats["fields"] = stats["fields"]/5.0 * 100 if stats["fields"] <= 5  else 100
        stats["records"] = stats["records"]/100.0 * 100 if stats["records"] <= 100  else 100
        stats["records_label"] = grading(stats["records"])
        stats["fields_label"] = grading(stats["fields"])
        stats["content_label"] = grading(stats["content"])
    stats["metadata_label"] = grading(stats["metadata"])
    stats["description_label"] = grading(stats["description"])
    stats["license"] = "license_url" in stats["ds"] and stats["ds"]["license_url"] != ""
    stats["version"] = "version" in stats["ds"] and stats["ds"]["version"] != ""
    stats["date_updated"] = dateutil.parser.parse(stats["ds"]["metadata_modified"])
    stats["last_updated"] = (datetime.datetime.now() - stats["date_updated"]).days
    return stats

def checkOccurenceFrequency(values,textcolumns):

    if not values:
        return {}

    ExitColumns=[]

    Json = values['result']

    TEMP = json.dumps(Json['records'])
    JsonData = pd.read_json(TEMP)
    textData = JsonData[textcolumns]

    for column in textData: #Checks if column has duplicates; if all values are unique -> result will be 0
        if (len(textData[textData.duplicated([column], keep=False)]) ==0):
            ExitColumns.append([column.encode("utf-8"), False])

    return ExitColumns ##that columns will be removed from rresource fields


def dataset(request, dataset_id):


    template_name = 'browser/dataset.html'

    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )

    textcolumns=[]
    resource_id = None 
    resource_fields = None
    related_datasets = None
    fields = None
    compleness = {}
    stats = {}
    data = None

    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )

        stats["ds"] = dataset

        try:
            url = settings.CKAN_URL + "/api/3/util/tet/get_recommended_datasets?pkg=" + dataset_id
            res = urlopen(url)
            related_datasets = json.loads(res.read())["datasets"]
        except Exception as e:
            messages.add_message(request, messages.ERROR, e)
            return render(request, error_template)
        if "resources" in dataset.keys():
            for resource in dataset["resources"]:
                if resource["format"].lower() in ["csv","xls"]:
                    dataset["has_table"] = True

                if resource["format"].lower()  == "pdf":
                    dataset["has_pdf"] = True
                if resource["format"].lower() in ["csv","xls"]:
                    try:
                        resource_id = resource["id"]
                        url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=99999"
                        res = urlopen(url)
                        data = json.loads(res.read())
                        resource_fields = []
                        filter_list = ["long", "lat", "no.", "phone", "date","id", "code"]
                        stats["fields"] = len(data["result"]["fields"])
                        stats["records"] = data["result"]["total"]
                        df = json_normalize(data["result"]["records"])
                        nullvalues = float(sum([v for v in df.isnull().sum()]))
                        allvalues = float(len(df.index)*len(df.columns))
                        stats["content"] = ((allvalues-nullvalues)/allvalues) * 100

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
                                textcolumns.append(name)
                            else:
                                pass
                        fields = data["result"]["fields"]
                        break
                    except Exception as e:
                        resource_fields = []
        completness = compute_completeness(stats)
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
        return render(request, error_template)
    uniqueColumns = checkOccurenceFrequency(data, textcolumns)
    if resource_id and len(resource_fields) < 1:
        resource_id = None
        ######
    if uniqueColumns: ##if there are any columns with unique values
        for column in uniqueColumns:
            for element in resource_fields:
                if (column[0].encode("utf-8") in element[0].encode("utf-8")):
                    resource_fields.remove(element)
    context = {
        'dataset_id': dataset_id,
        'dataset': dataset,
        'completness' : completness,
        'metadata_box': dataset_to_metadata_text(dataset),
        'spod_box_datasets': dataset_to_spod(dataset),
        'resource_fields': resource_fields,
        'related_datasets' : related_datasets,
        'CKAN_URL': settings.CKAN_URL + "/dataset/" + dataset_id + "?r=" + request.get_full_path(),
        'fields' : resource_fields_to_text(fields)
    }
    if resource_id:
        context['resource_id'] = resource_id
        context['freq_resource_id'] = "/en/api/table/" + resource_id
    return render(request, template_name, context)

def box_plot(request, resource_id):
    try:
        url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=99999"
        res = urlopen(url)
        data = json.loads(res.read())
        df = json_normalize(data["result"]["records"])
        fields = data["result"]["fields"]
        numeric_fields = [f["id"] for f in fields if f["type"] == "numeric"]
        df[numeric_fields] = df[numeric_fields].apply(pd.to_numeric)
        del df["_id"] 
        color = dict(boxes='#2196F3', whiskers='#2196F3', medians='#007DBE', caps='#2196F3')
        with mutex:
            box = df.plot.box(color=color)
            plt.subplots_adjust(bottom=0.25)
            plt.xticks(rotation=90)
            plt.tight_layout()
            fig = box.get_figure()
            fig.set_facecolor('white')
            canvas = FigureCanvas(fig)
            response = HttpResponse(content_type='image/png')
            canvas.print_png(response)
        return response
    except Exception as e:
        return JsonResponse({'message': str(e)})

def corr_mat(request, resource_id):
    try:
        url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=99999"
        res = urlopen(url)
        data = json.loads(res.read())
        df = json_normalize(data["result"]["records"])
        fields = data["result"]["fields"]
        numeric_fields = [f["id"] for f in fields if f["type"] == "numeric"]
        df[numeric_fields] = df[numeric_fields].apply(pd.to_numeric)
        del df["_id"] 
        corr = df.corr()
        with mutex:
            fig, ax = plt.subplots()
            cax = ax.matshow(corr)
            fig.colorbar(cax)
            plt.xticks(range(len(corr.columns)), corr.columns);
            plt.yticks(range(len(corr.columns)), corr.columns);
            plt.xticks(rotation=90)
            plt.tight_layout()
            fig.set_facecolor('white')
            canvas = FigureCanvas(fig)
            response = HttpResponse(content_type='image/png')
            canvas.print_png(response)
        return response
    except Exception as e:
        return JsonResponse({'message': str(e)})

def get_dataset(dataset_id):
    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )
    url = settings.CKAN_URL + "/dataset/" + dataset_id
    resource_id = None
    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
        return dataset
    except Exception as e:
        return None

def get_resource_data(resource_id, limit = 0):
        url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=" + str(limit)
        res = urlopen(url)
        return json.loads(res.read())

def exe_sql(sql):
        url = settings.CKAN_URL + "/api/action/datastore_search_sql?sql=" + urllib.quote(sql)
        res = urlopen(url)
        return json.loads(res.read().decode('utf-8'))

def download(request):
    sql = None
    if request.method == 'POST':
        sql = request.POST.get("sql", "")
        data = exe_sql(sql)
        df = pd.DataFrame()
        if len(data["result"]["records"]) > 0:
            df = json_normalize(data["result"]["records"])
            del df["_id"]
            del df["_full_text"]
            fields = data["result"]["fields"]
            headers = [field["id"]for field in fields ].remove("_id")
        sio = StringIO()
        df.to_csv(sio,  index=False)
        filename = "data.csv"
        workbook = sio.getvalue()
        response = StreamingHttpResponse(workbook, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

def create_trigger(request):
    if request.method == 'POST':
        success  = True
        message = ""
        sql = request.POST.get("sql", "")
        email = request.POST.get("email", "")
        notification =  request.POST.get("notification", "")
        if email == "":
            message = _("Email")
            success = False
        if notification == "":
            if not success:
                message += " " + _("and") + " "
            message += _("Notification\n")
            success = False

        if not success:
            message = _("Missing: ") +  message
            return JsonResponse({
            "success" : success,
            "message" : message
            })

        message = _("Alert created successfully") 
        try:
            conn = sqlite3.connect(settings.DB)
            c = conn.cursor()
            c.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='triggers';''')
            if not c.fetchone():
                c.execute('''CREATE TABLE triggers (id INTEGER PRIMARY KEY,email text, notification text, query text)''')
            try:
                c.execute("""INSERT INTO  triggers VALUES (NULL, ?,?,?)""",(email, notification,sql))
                conn.commit()
            except Exception as e:
                success = False
                message = _("Error: " + str(e))
                conn.rollback()
                return JsonResponse({
                    "success" : success,
                    "message" : message
                })
        except Exception as e:
            print(str(e))
            success = False
            message = _("Error: " + str(e))
        return JsonResponse({
            "success" : success,
            "message" : message
        })


def combine(request, dataset_id = False):
    template_name = 'browser/merge.html'
    selected_datasets = []
    groups = {"other": []}
    base_dataset = None
    base_dataset_resource_id = None
    API_LINK = None

    try:

        if (dataset_id):
            base_dataset = get_dataset(dataset_id)

            if "resources" in base_dataset.keys():
                for resource in base_dataset["resources"]:
                    # TODO multiple resources view
                    if resource["format"].lower() in ["csv","xls"]:
                        base_dataset_resource_id = resource["id"]
                        API_LINK = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + base_dataset_resource_id + "&limit=99999"

        if 'merge' in request.POST:
            rs = request.POST.getlist('selected_rs')
            if len(rs) > 0:
                sql = ""
                for r in rs:
                    if len(sql) > 0:
                        sql += " UNION "
                    sql += "SELECT * , '" + r.split(",")[1] + "' as File from \"" + r.split(",")[0] + "\""
                data = exe_sql(sql)
                df = json_normalize(data["result"]["records"])
                del df["_id"]
                del df["_full_text"]
                fields = data["result"]["fields"]
                headers = [field["id"]for field in fields].remove("_id")
                sio = StringIO()
                df.to_csv(sio,  index=False)
                filename = "merged.csv"
                workbook = sio.getvalue()
                response = StreamingHttpResponse(workbook, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response

        if 'analyse' in request.POST:
            rs = request.POST.getlist('selected_rs')
            if len(rs) > 0:
                sql = ""
                for r in rs:
                    if len(sql) > 0:
                        sql += " UNION "
                    sql += "SELECT * , '" + r.split(",")[1] + "' as File from \"" + r.split(",")[0] + "\""
                url = settings.CKAN_URL + "/api/action/datastore_search_sql?sql=" + urllib.quote(sql)
                context = {
                    "RESOURCE_URL" : url,
                    "ACTION" : "analyse",
                    
                }
                template_name = 'browser/analyse.html'
                return render(request, template_name, context)

        if 'view' in request.POST:
            rs = request.POST.getlist('selected_rs')
            if len(rs) > 0:
                sql = ""
                for r in rs:
                    if len(sql) > 0:
                        sql += " UNION "
                    sql += "SELECT * , '" + r.split(",")[1] + "' as File from \"" + r.split(",")[0] + "\""
                url = settings.CKAN_URL + "/api/action/datastore_search_sql?sql=" + urllib.quote(sql)

                context = {
                    "RESOURCE_URL" : url,
                    "ACTION" : "view"
                }

                template_name = 'browser/analyse.html'
                return render(request, template_name, context)

        if 'chart' in request.POST:
            rs = request.POST.getlist('selected_rs')
            if len(rs) > 0:
                sql = ""
                for r in rs:
                    if len(sql) > 0:
                        sql += " UNION "
                    sql += "SELECT * from \"" + r.split(",")[0] + "\""
                url = settings.CKAN_URL + "/api/action/datastore_search_sql?sql=" + urllib.quote(sql)
                data = get_resource_data(rs[0].split(",")[0])
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
                context = {
                    "RESOURCE_URL" : url,
                    "ACTION" : "chart",
                    "resource_fields" : resource_fields
                }
                context['freq_resource_id'] = "/en/api/query/" + urllib.quote(sql)
                template_name = 'browser/analyse.html'
                return render(request, template_name, context)

        if 'combine_datasets' in request.POST:

            selected_datasets = request.POST.getlist('selected_datasets')

            if base_dataset["id"]:
                selected_datasets.insert(0, base_dataset["id"])

            # get unique values
            selected_datasets = set(selected_datasets)
            selected_datasets = list(selected_datasets)

            for dataset_id in selected_datasets:
                dataset = get_dataset(dataset_id)
                if "resources" in dataset.keys():
                    for resource in dataset["resources"]:
                        if resource["format"].lower() in ["csv","xls"]:
                            resource_id = resource["id"]                 
                            try:
                                fields = "_".join([f["id"] for f in get_resource_data(resource_id)["result"]["fields"]])
                            except Exception:
                                fields = "other"
                            if fields not in groups.keys():
                                groups[fields] = []
                            groups[fields].append({"title": dataset["title"], "resource_id": resource_id, "name": resource["name"], "format": resource["format"]})

                else:
                    groups["other"].append(dataset)
        for g in groups.keys():
            if len(groups[g]) < 2:
                if g == "other":
                    continue
                groups["other"].extend(groups[g])
                del groups[g]
    except Exception as e:
        return JsonResponse({'message': str(e)})
    context = {
        "dataset_groups" : groups,
        "base_dataset" : base_dataset,
        "base_dataset_resource_id" : base_dataset_resource_id,
        "dataset_id" : dataset_id,
        'API_LINK' : API_LINK,
        'QUERY_API': settings.CKAN_URL + "/api/action/datastore_search_sql"
     }

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
    resource_fields = None
    numeric_fields = None

    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
        if "resources" in dataset.keys():
            for resource in dataset["resources"]:

                if resource["format"].lower()  == "pdf":
                    dataset["has_pdf"] = True

                if resource["format"].lower() in ["csv","xls"]:
                    views = ckan_api_instance.action.resource_view_list(id=resource["id"])
                    resource_id = resource["id"]
                    url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=1"
                    res = urlopen(url)
                    data = json.loads(res.read())
                    resource_fields = data["result"]["fields"]
                    numeric_fields = [f["id"] for f in resource_fields if f["type"] == "numeric"]

                    for view in views:
                        if (view["view_type"]=="recline_view"):
                            url_table = settings.CKAN_URL + "/dataset/" + dataset_id + "/resource/" + resource["id"] + "/view/" + view["id"]
                            break
                    for view in views:
                        if (view["view_type"]=="pivottable"):
                            url_pivottable = settings.CKAN_URL + "/dataset/" + dataset_id + "/resource/" + resource["id"] + "/view/" + view["id"]
                            pivot_resource_url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=9999"
                            pivot_res = urlopen(pivot_resource_url)
                            pivot_resource_json = json.loads(pivot_res.read())
                            break
                    break
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
        return render(request, error_template)
    context = {
        "url_table": url_table,
        'url_pivottable': url_pivottable,
        'dataset_id': dataset_id,
        'dataset': dataset,
        'metadata_box': dataset_to_metadata_text(dataset),
        'spod_box_datasets': dataset_to_spod(dataset),
        'CKAN_URL': settings.CKAN_URL + "/dataset/" + dataset_id + "?r=" + request.get_full_path(),
        'API_LINK' : settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=99999", 
        'QUERY_API': settings.CKAN_URL + "/api/action/datastore_search_sql",
        'resource_id' : resource_id,
        'resource_fields' : resource_fields,
        'numeric_fields' : numeric_fields,
        'pivot_resource_json': json.dumps(pivot_resource_json['result']['records']),
     }

    return render(request, template_name, context)

def dataset_as_summary(request, dataset_id):
    template_name = 'browser/summary.html'
    resource_id = None
    fields_description = None   
    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )
    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
        if "resources" in dataset.keys():
            for resource in dataset["resources"]:
                if resource["format"].lower() in ["csv","xls"]:
                    resource_id = resource["id"]
                    url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=99999"
                    res = urlopen(url)
                    data = json.loads(res.read())
                    df = json_normalize(data["result"]["records"])
                    fields = data["result"]["fields"]
                    numeric_fields = [f["id"] for f in fields if f["type"] == "numeric"]
                    df[numeric_fields] = df[numeric_fields].apply(pd.to_numeric)
                    del df["_id"]
                    desc = df.describe()
                    fields_description ={}
                    for d in desc:
                        fields_description[d]=dict(desc[d])
                    break

    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
        return render(request, error_template)

    context = {
        "resource_id" : resource_id,
        "fields_description" : fields_description,
        "dataset" : dataset,
        'CKAN_URL': settings.CKAN_URL + "/dataset/" + dataset_id + "?r=" + request.get_full_path(),
    }
    return render(request, template_name, context)

def cache_db(key, value=None):
    mutex.acquire()
    data = {}
    file_name = "cache/" + key + ".d"
    if value == None:
        try:
            data = pickle.load(open(file_name,"rb"))
        except IOError:
            pass
    else:
       pickle.dump(value, open(file_name,"wb"))
    mutex.release()
    return data

def text_analytics(dataset_id, url, notes):
    cache_response = cache_db(dataset_id)
    if len(cache_response) > 0:
        return cache_response
    else:
        data = None
        try:
            remote_file = urlopen(url).read()
            memory_file = StringIO(remote_file)
            pdf_to_read = PdfFileReader(memory_file)
            raw_text = notes
            for pageNum in xrange(pdf_to_read.getNumPages()):
                try:
                    raw_text += pdf_to_read.getPage(pageNum).extractText()
                except Exception:
                    continue
            alchemy_language = AlchemyLanguageV1(api_key=settings.API_KEY)
            data = alchemy_language.combined(raw_text, extract="concepts dates title keywords relations entities", max_items=10)
            summary = set()
            for relation in data["relations"]:
                if relation["sentence"] not in summary:
                    summary.add(relation["sentence"])
            data ["summary"] = summary
            cache_db(dataset_id,data)
        except Exception as e:
            pass
        return data

def dataset_as_pdf(request, dataset_id):
    template_name = 'browser/pdf.html'
    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )
    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
        if "resources" in dataset.keys():
            for resource in dataset["resources"]:
                if resource["format"].lower() == "pdf":
                    _text_analytics = text_analytics(dataset_id, resource["url"], dataset["notes"])
                    context = {
                       "dataset" : dataset,
                       "url" : resource["url"],
                       "text_analytics" : _text_analytics
                    }
                    return render(request, template_name, context)
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
        return render(request, error_template)

def data_cards(request):
    template_name = 'browser/data_cards.html'
    indicators = []

    # TODO move to helper function
    try:
        for indicator in settings.INDICATORS:
            try:
                url = settings.CKAN_URL + "/api/action/datastore_search_sql?sql=" + urllib.quote(indicator["query"])
                res = urlopen(url)
                data = json.loads(res.read().decode('utf-8'))

                results = []

                for kw in data["result"]["records"]:
                    kw["title"] = indicator["title"]
                    results.append(kw)

                # TODO add class / icon in config model
                indicators.append({"key": indicator["title"], "cards": results, "class": "TODO"})

            except Exception as e:
                pass
    except Exception as e:
        pass

    context = {
        'indicators': indicators,
    }

    return render(request, template_name, context)

def dashboard(request):
    template_name = 'browser/dashboard/index.html'

    context = {

    }

    return render(request, template_name, context)
