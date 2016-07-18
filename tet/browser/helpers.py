from django.conf import settings

# TODO consider migration to /tet/


def metadata_to_text(dataset):
    text =  'This Dataset was created at <strong>22nd July 2015</strong> and was last updated on <strong>14 March 2016</strong>. The dataset is available in the following formats: <strong>CSV</strong> and <strong>DOCX</strong>. The dataset can be used under <strong>Creative Commons License</strong>. In you need more details please contact <a href="#" data-original-title="" title="">info@dublin-tet.com</a>.'
    return text
