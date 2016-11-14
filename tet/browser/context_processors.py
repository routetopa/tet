from django.conf import settings


def common_settings(request):
    return {
        'CKAN_URL': settings.CKAN_URL,
        'SPOD_URL': settings.SPOD_URL,
    }

