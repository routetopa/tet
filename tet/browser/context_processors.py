from django.conf import settings


def common_settings(request):
    return {
        'SPOD_URL': settings.SPOD_URL
    }

