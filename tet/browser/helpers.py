from django.conf import settings
from dateutil.parser import parse

# TODO consider migration to /tet/

# Generates user friendly metadata description fo the dataset: creation, categories etc.
def metadata_to_text(dataset):
    '''
    :param dataset: CKAN API response - JSON representation of dataset
    :return: string
    '''

    # print(dataset)

    text = "<p>This Dataset was created at <strong>" + parse(dataset["metadata_created"]).strftime("%d %B% %Y, %H:%M") + "</strong>"
    text += " and last modified at <strong>" + parse(dataset["metadata_modified"]).strftime("%d %B% %Y, %H:%M") + "</strong>.</p>"

    if dataset["license_title"]:
        text += "<p>This Dataset is published under <strong>" + dataset["license_title"] + "</strong> license.</p>"

    if dataset["organization"]:
        text += "<p>The data was published by <strong>" + dataset["organization"]["title"] + "</strong>.</p>"

    if dataset["maintainer_email"]:
        text += "<p>In you need more details, maintainer can be contacted at: <a href='#' data-original-title='' title=''><strong>" + dataset["maintainer_email"] + "</strong></a>.</p>"

    if dataset["num_resources"] > 0:
        text += "<p>The data is available in " + str(dataset["num_resources"]) + " format"
        if dataset["num_resources"] > 1:
            text += "s"

        text += ": ";

        # TODO direct link
        for res in dataset["resources"]:
            text += "<strong>" + res["format"] + "</strong> "

        text += "</p>"

    return text



# Generates Dataset URL bases on SETTINGS and dataset name / permalink
def name_to_url(name):
    '''
    :param name: dataset 'name', url permalink
    :return: url
    '''
    return settings.CKAN_URL + "/dataset/" + name

