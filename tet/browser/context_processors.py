from django.conf import settings


def common_settings(request):
    return {
        'CKAN_URL': settings.CKAN_URL,
        'SPOD_URL': settings.SPOD_URL,
        'SOM_API_URL': settings.SOM_API_URL,
        'GA_API_KEY': settings.GA_API_KEY,
        'TET_VERSION': settings.TET_VERSION,
    }

