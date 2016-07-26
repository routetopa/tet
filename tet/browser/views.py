#-*- coding: utf-8 -*-

import ckanapi
import re

import os


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

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()

def index(request):
    return render(request, 'browser/index.html')


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
        periods ={}
        locations ={}
        locations_list = ["Dublin" , "Leinster", "Cork", "Munster", "Limerick", "Waterford", "Kilkenny", "Galway" ]

        for idx, dataset in enumerate(api_result["results"]):
            # bold the query phrase
            dataset["title"] = pattern.sub("<strong>"+query+"</strong>", strip_tags(dataset["title"]))
            dataset["notes"] = pattern.sub("<strong>"+query+"</strong>", strip_tags(dataset["notes"]))

            # used in search / filtering JS
            dataset["relevance_key"] = idx
            dataset["name_key"] = strip_tags(dataset["title"])[:10].upper()
            dataset["date_key"] = parse(dataset["metadata_created"]).strftime("%Y%m%d%H%M%S")

            search_results.append(dataset)

            text = (dataset["title"] + dataset["notes"]).lower()

            if "category" in dataset.keys():
                if dataset["category"] not in themes.keys():
                    themes[dataset["category"]] = 1
                else:
                    themes[dataset["category"]] += 1
            for year in range (1900, 2020):
                syear = str(year)
                if text.find(syear) > 0:
                    if syear not in periods.keys():
                        periods[syear] = 1
                    else:
                        periods[syear] += 1

            for location in locations_list:
                slocation = location.lower() 
                if text.find(slocation) > 0:
                    if location not in locations.keys():
                        locations[location] = 1
                    else:
                        locations[location] += 1

        if "" in themes.keys():
            del themes[""]
        filters["themes"] = themes 
        filters["locations"] = locations
        filters["periods"] = periods
        
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

    try:
        dataset = ckan_api_instance.action.package_show(
            id=dataset_id
        )
    except:
        raise Http404("No Dataset found.")

    context = {
        'dataset_id': dataset_id,
        'dataset': dataset,
        'metadata_box': dataset_to_metadata_text(dataset),
        'spod_box': dataset_to_spod(dataset),
        'SPOD_URL': settings.SPOD_URL,
    }

    return render(request, template_name, context)


def dataset_as_app(request, dataset_id):
    return HttpResponse(dataset_id + ' as_app')


def dataset_as_table(request, dataset_id):
    return HttpResponse(dataset_id + ' as_table')

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
