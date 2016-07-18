#-*- coding: utf-8 -*-

import ckanapi
import html
import re
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.views import generic
from reportlab.pdfgen import canvas
from io import BytesIO


def index(request):
    return render(request, 'browser/index.html')


# TODO url param parsing
# TODO pagination
def search(request, query=False):

    template_name = 'browser/search.html'

    # display logic
    query = request.GET.get('query') or ''
    search_results = []
    filters = []
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
        for dataset in api_result["results"]:
            # bold the query phrase
            dataset["title"] = pattern.sub("<strong>"+query+"</strong>", html.escape(dataset["title"]))
            dataset["notes"] = pattern.sub("<strong>"+query+"</strong>", html.escape(dataset["notes"]))

            #|truncatewords:55
            search_results.append(dataset)


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


    # display logic
    search_results = []
    filters = []
    has_results = False


    context = {
        'dataset_id': dataset_id,
    }

    return render(request, template_name, context)

def pdf_generaton_sample(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response