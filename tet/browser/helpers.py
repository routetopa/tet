# -*- coding: utf-8 -*-

from django.conf import settings
from dateutil.parser import parse
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

import locale

try: 
  from urllib2 import urlopen
  from urlparse import scheme_chars
  unicode = unicode
except ImportError: 
  from urllib.request import urlopen

import json


# TODO consider migration to /tet/
# Generates user friendly metadata description fo the dataset: creation, categories etc.
def dataset_to_metadata_text(dataset):
    '''
    :param dataset: CKAN API response - JSON representation of dataset
    :return: string
    '''

    current_lang = get_language()

    if current_lang == "it":

        locale.setlocale(locale.LC_ALL, "it_IT")

        text = u"<p>Questo Dataset è stato creato il <strong>" + parse(dataset["metadata_created"]).strftime("%d %B% %Y, %H:%M") + u"</strong>"
        text += u" e l'ultima modifica è del <strong>" + parse(dataset["metadata_modified"]).strftime("%d %B% %Y, %H:%M") + u"</strong>.</p> "


        if dataset["license_title"]:
            text += u"<p>Questo Dataset è soggetto a licenza di pubblicazione <strong>" + dataset["license_title"] + u"</strong></p> "

        if dataset["organization"]:
            text += u"<p>I dati sono stati pubblicati da <strong>" + dataset["organization"]["title"] + u"</strong>.</p> "

        if dataset["maintainer_email"]:
            text += u"<p>Se avete bisogno di ulteriori dettagli, manutentore può essere contattato all'indirizzo: <a href='#' data-original-title='' title=''><strong>" + dataset["maintainer_email"] + u"</strong></a>.</p> "

        if dataset["num_resources"] > 0:
            text += u"<p>I dati sono disponibili in " + str(dataset["num_resources"]) + u" format"
            if dataset["num_resources"] > 1:
                text += u"i"

            text += u": ";

            # TODO direct link
            for res in dataset["resources"]:
                text += u"<strong>" + res["format"] + u"</strong> "

            text += u"</p> "

    # default lang - "en"
    else:
        text = "<p>This Dataset was created at <strong>" + parse(dataset["metadata_created"]).strftime("%d %B% %Y, %H:%M") + "</strong>"
        text += " and last modified at <strong>" + parse(dataset["metadata_modified"]).strftime("%d %B% %Y, %H:%M") + "</strong>.</p> "

        if dataset["license_title"]:
            text += "<p>This Dataset is published under <strong>" + dataset["license_title"] + "</strong> license.</p> "

        if dataset["organization"]:
            text += "<p>The data was published by <strong>" + dataset["organization"]["title"] + "</strong>.</p> "

        if dataset["maintainer_email"]:
            text += "<p>If you need more details, maintainer can be contacted at: <a href='#' data-original-title='' title=''><strong>" + dataset["maintainer_email"] + "</strong></a>.</p> "

        if dataset["num_resources"] > 0:
            text += "<p>The data is available in " + str(dataset["num_resources"]) + " format"
            if dataset["num_resources"] > 1:
                text += "s"

            text += ": ";

            # TODO direct link
            for res in dataset["resources"]:
                text += "<strong>" + res["format"] + "</strong> "

            text += "</p> "

    return text


# Get rooms related to DATASET
# List all the rooms per all the resources
def get_rooms_for_dataset(dataset):

    rooms = []
    rooms_ids = []

    if dataset["num_resources"] > 0:
        for res in dataset["resources"]:
            # TODO results merging / checking for duplicates
            try:
                url = settings.SPOD_URL + "/spodapi/roomsusingdataset?data-url=" + \
                settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + res["id"]

                print(url)

                req = urlopen(url)
                content = req.read().decode('utf8')
                j = json.loads(content)

                if j["status"] == "success" and j["result"]:
                    for room in j["result"]:
                        # check for unique rooms numbers
                        if not room["id"] in rooms_ids:
                            rooms.append(room)
                            rooms_ids.append(room["id"])
            except Exception, e:
                # do nothing
                print("Error: " + str(e))
                pass

    return rooms


# Generates list of SPOD rooms for discussions widget
def dataset_to_spod(dataset):

    rooms = get_rooms_for_dataset(dataset)

    if rooms:
        for room in rooms:

            try:
                url = settings.SPOD_URL + "/spodapi/roomsummary?id=" + str(room["id"])
                req = urlopen(url)
                content = req.read().decode('utf8')
                j = json.loads(content)

                # print(j)

                if j["status"] == "success" and j["result"]:
                    room["roomsummary"] = j["result"]
                else:
                    room["roomsummary"] = False
            except Exception, e:
                # do nothing
                print("Error: " + str(e))
                pass

    return rooms


# Generates Dataset URL bases on SETTINGS and dataset name / permalink
def name_to_url(name):
    '''
    :param name: dataset 'name', url permalink
    :return: url
    '''
    return settings.CKAN_URL + "/dataset/" + name


# make fields type name user friendly
# see: http://docs.ckan.org/en/latest/maintaining/datastore.html#fields

def resource_fields_to_text(resource_fields):

    field_switcher = {
        "int": "Integer numbers, e.g 42, 7",
        "int4": "Integer numbers, e.g 42, 7",
        "numeric": "Numbers, e.g 1, 2.4, 4.7",
        "float": "Floats, e.g. 1.61803",
		"text": "Arbitrary text data, e.g. Some text",
		"json": "Arbitrary nested json data",
		"date": "Date without time, e.g 2016-5-25",
		"time": "Time without date, e.g 12:06",
		"timestamp": "Date and time, e.g 2016-05-01T02:43Z",
		"bool": "Boolean values, e.g. true, 0",
    }

    if (resource_fields):
        for field in resource_fields:
            field["type_unified"] =  field_switcher.get(field["type"], "Other: " + field["type"])

    return resource_fields
