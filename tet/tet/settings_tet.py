# DATA SOURCE: CKAN - Comprehensive Knowledge Archive Network
# Required
CKAN_URL = "http://dublin-tet.routetopa.eu:8080"

# Optional
CKAN_USERNAME = "username"
CKAN_API_KEY = "xxxx-xxxx-xxxx-xxxx"

# SPOD - SOCIAL PLATFORM ON OPEN DATA
SPOD_URL = "http://dublin-spod.routetopa.eu"

# TET
TET_VERSION = "3.0"

# Homepage
TET_SIMPLE_HOMEPAGE = False

# Google Analytics
GA_API_KEY = False

LOGIN_URL = '/accounts/login/'

LOCATIONS_LIST = ["Dublin", "Leinster", "Cork", "Munster", "Limerick", "Waterford", "Kilkenny", "Galway", "Prato", "Paris", "Daan Haag"]

INDICATORS =[
  { "title" : "Dublin City Spendings",
  "query":"SELECT \"ServiceType\" as key, sum(\"AdoptedbyCouncil2014\") as value from \"31cc6276-62d9-4bec-9fcc-0f0acb2a6662\" Group By \"ServiceType\""}
]

# datasets recommendation API for TET
SOM_API_URL = "http://vmrtpa05.deri.ie:8004"

DB = "triggers.db"

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        # directory path should be absolute
        'LOCATION': '/var/tmp/tet-temp-cache',
        # for Windows servers
        # 'LOCATION': 'c:/foo/bar',
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
