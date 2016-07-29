#-*- coding: utf-8 -*-

import ckanapi
import re

import os

import urllib
import json
from .helpers import dataset_to_metadata_text, dataset_to_spod, name_to_url
from io import BytesIO
from dateutil.parser import parse

from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.utils.html import strip_tags
from django.views import generic

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from django.shortcuts import render, redirect

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()

def index(request):

    template_name = 'browser/index.html'

    try:

        url_datasets = settings.CKAN_URL + "/api/3/stats/dataset_count"
        url_organizations = settings.CKAN_URL + "/api/3/stats/organization_count"

        res_datasets = urllib.request.urlopen(url_datasets)
        datasets_count_json = json.loads(res_datasets.read().decode(res_datasets.info().get_param('charset') or 'utf-8'))
        datasets_count = int(datasets_count_json['dataset_count'])

        res_organizations = urllib.request.urlopen(url_organizations)
        organizations_count_json = json.loads(res_organizations.read().decode(res_organizations.info().get_param('charset') or 'utf-8'))
        organizations_count = int(organizations_count_json['organization_count'])

    except Exception:
        datasets_count = 0
        organizations_count = 0
        pass

    context = {
        'datasets_count': datasets_count,
        'organizations_count': organizations_count,
        'CKAN_URL': settings.CKAN_URL,
    }

    return render(request, template_name, context)


# TODO url param parsing
# TODO pagination
def search(request, query=False):

    template_name = 'browser/search.html'

    # display logic
    query = request.GET.get('query') or ''
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

        locations_list = ["Dublin", "Leinster", "Cork", "Munster", "Limerick", "Waterford", "Kilkenny", "Galway" ]

        for idx, dataset in enumerate(api_result["results"]):
            # bold the query phrase
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

        filters["themes"] = themes 
        filters["locations"] = locations
        filters["periods"] = periods
        filters["formats"] = formats

    context = {
        'query': query,
        'has_results': has_results,
        'search_results': search_results,
        'filters': filters,
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
    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
        if "resources" in dataset.keys():
            for resource in dataset["resources"]:
                if resource["format"].lower() in ["csv","xls"]:
                    try:
                        resource_id = resource["id"]
                        url = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=5"

                        res = urllib.request.urlopen(url)
                        data = json.loads(res.read().decode(res.info().get_param('charset') or 'utf-8'))
                        fields = []
                        filter_list = ["long", "lat", "no.", "phone", "date","id"] 
                        for field in data["result"]["fields"]:
                            name = field["id"]
                            found = False 
                            for f in filter_list:
                                if f in name.lower():
                                    found = True 
                            if found:
                                continue
                            if field["type"] == "numeric":
                                fields.append((name, True))
                            elif field["type"] == "text":
                                fields.append((name, False))
                            else:
                                pass
                        resource_fields = fields
                        resource_id = settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + resource_id + "&limit=9999"
                        break
                    except Exception:
                        resource_id = None
                        resource_fields = None 
                        pass
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
        'resource_id':resource_id,
        'resource_fields': resource_fields
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
    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
        if "resources" in dataset.keys():
            for resource in dataset["resources"]:
                if resource["format"].lower() in ["csv","xls"]:
                    views = ckan_api_instance.action.resource_view_list(id=resource["id"])
                    for view in views:
                        if (view["view_type"]=="recline_view"):
                            url = settings.CKAN_URL + "/dataset/" + dataset_id + "/resource/" + resource["id"] + "/view/" + view["id"]
                            break
    except Exception:
        raise Exception

    context = {
        'url': url
    }

    return render(request, template_name, context)

# TODO summary: keywords, charts, extracted media
def dataset_as_pdf(request, dataset_id):

    ckan_api_instance = ckanapi.RemoteCKAN(
        settings.CKAN_URL,
        user_agent='tetbrowser/1.0 (+http://tetbrowser.routetopa.eu)'
    )


    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
    except:
        raise Http404("No Dataset found.")

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dataset_summary_by_tet.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)

    # Draw summary on the PDF
    # See the ReportLab documentation for the full list of functionality.

    style = styles["Normal"]
    style.alignment = TA_JUSTIFY

    # Document title
    p.setFillColorCMYK(1, 0.342, 0, 0.106)                                          # choose font colour
    p.setFont("Helvetica", 19)                                                      # choose font type and font size
    p.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT - 1.5 * inch, dataset["title"]) # write text

    # Document notes
    paragraph = Paragraph(dataset["notes"], style)
    paragraph.wrapOn(p, PAGE_WIDTH - 2 * inch, PAGE_HEIGHT - 2 * inch)
    paragraph.drawOn(p, 1 * inch, PAGE_HEIGHT - 3 * inch)

    # Draw ROUTE-TO-PA project logo
    filename = settings.STATIC_ROOT + "/images/logo-RTPA-150.png"
    p.drawImage(filename, 0.25 * inch, 0.25 * inch, 0.5 * inch, 0.5 * inch)
    p.setFont('Helvetica',9)
    p.drawString(0.85 * inch, 0.55 * inch, "Document generated by TET / ROUTE-TO-PA project")
    p.setFillColorCMYK(0, 0, 0, 0.55) # choose your font colour
    p.drawString(0.85 * inch, 0.4 * inch, "Data source: " + name_to_url(dataset["name"]))

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
