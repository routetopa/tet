from django.conf import settings
from dateutil.parser import parse

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

    # print(dataset)

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

    if dataset["num_resources"] > 0:
        for res in dataset["resources"]:
            # TODO results merging / checking for duplicates
            try:
                url = settings.SPOD_URL + "/spodapi/roomsusingdataset?data-url=" + \
                settings.CKAN_URL + "/api/action/datastore_search?resource_id=" + res["id"]

                # print(url)

                req = urlopen(url)
                content = req.read().decode('utf8')
                j = json.loads(content)

                if j["status"] == "success" and j["result"]:
                    rooms.append(j["result"][0])
            except:
                # do nothing
                pass

    return rooms


# Generates list of SPOD rooms for discussions widget
def dataset_to_spod(dataset):

    rooms = get_rooms_for_dataset(dataset)

    if rooms:
        for room in rooms:

            try:
                url = settings.SPOD_URL + "/spodapi/roomsummary?id=" + str(room["id"])
                print(url)
                req = urlopen(url)
                content = req.read().decode('utf8')
                j = json.loads(content)

                # print(j)

                if j["status"] == "success" and j["result"]:
                    room["roomsummary"] = j["result"]
                else:
                    room["roomsummary"] = False
            except:
                # do nothing
                pass

    print(rooms)

    return rooms


# Generates Dataset URL bases on SETTINGS and dataset name / permalink
def name_to_url(name):
    '''
    :param name: dataset 'name', url permalink
    :return: url
    '''
    return settings.CKAN_URL + "/dataset/" + name

