
# DATA SOURCE: CKAN - Comprehensive Knowledge Archive Network
# Required
CKAN_URL = "http://dublin-tet.routetopa.eu:8080"

# Optional
CKAN_USERNAME = "admin"
CKAN_API_KEY = "xxxx-xxxx-xxxx-xxxx"

# SPOD - SOCIAL PLATFORM ON OPEN DATA
SPOD_URL = "http://dublin.routetopa.eu"

# TET

# Homepage
TET_SIMPLE_HOMEPAGE = False

# Google Analytics
GA_API_KEY = False



# TODO cleanup

API_KEY = "xxxx-xxxx-xxxx-xxxx"

LOGIN_URL = '/accounts/login/'

LOCATIONS_LIST = ["Dublin", "Leinster", "Cork", "Munster", "Limerick", "Waterford", "Kilkenny", "Galway", "Prato", "Paris", "Daan Haag"]

INDICATORS =[
  { "title" : "Dublin City Spendings",
  "query":"SELECT \"ServiceType\" as key, sum(\"AdoptedbyCouncil2014\") as value from \"31cc6276-62d9-4bec-9fcc-0f0acb2a6662\" Group By \"ServiceType\""}
]

SOM_API_URL = "http://vmrtpa05.deri.ie:8006"

DB = "triggers.db"
