Transparency-Enhancing Toolset 3.0
===============

TET interface developed for ROUTE-TO-PA project

Requirements
------------

- [Python](https://www.python.org/downloads)
- [Django 1.9](https://www.djangoproject.com)
- [ckan/ckanapi](https://github.com/ckan/ckanapi)


Getting Started
---------------

### Initial Setup ###
1. Make a new virtualenv: ``virtualenv -p python venv``
2. Activate the virtualenv: ``source venv/bin/activate``
3. Install dependencies from requirements.txt i.e. ``pip install -r requirements.txt``
4. OPTIONAL: Generate RSA key  ``python manage.py creatersakey``
5. Run migrations ``python manage.py migrate``
6. Run the server: ``python manage.py runserver``
7. Open website in browser at ``http://localhost:8000``


### After initial setup ###
1. Activate the virtualenv: ``source venv/bin/activate``
2. Run the server: ``python manage.py runserver``
3. Open website in browser at ``http://localhost:8000``

### Configuration ###

TET configuration file is available at ``tet/tet/settings_tet.py``.
Main configuration options are as follows:

- ``CKAN_URL`` - URL of the CKAN instance
- ``SPOD_URL``  - URL of the SPOD Platform
- ``SOM_API_URL`` - URL of datasets recommendation API for TET
- ``GA_API_KEY`` - Google Analytics API key
- ``CACHES :: LOCATION`` - The path should be absolute. Please make sure that the selected directory exists and is readable and writable by the system user under which Web server runs.
- ``USE_SPOD_CHARTS`` - Indicator which visualisations should be use. By default it is set True

### Acknowledgement ###
Development of this project is supported by European Commision through the [ROUTE-TO-PA project](http://routetopa.eu/)
