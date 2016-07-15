#-*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import generic

from reportlab.pdfgen import canvas
from io import BytesIO


def index(request):
    return render(request, 'browser/index.html')


def search(request, query):

    template_name = 'browser/search.html'

    context = {
        'query': query,
    }

    return render(request, template_name, context)


def dataset(request, dataset_id):

    template_name = 'browser/index.html'

    context = {
        'latest_question_list': {'asd', 'fgs', dataset_id},
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