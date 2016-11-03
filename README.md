django-tet-ui
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
3. Install dependencies from requirements.txt i.e. ``pip install {lib name}``
4. Generate RSA key  ``python manage.py creatersakey``
5. Run migrations ``python manage.py migrate``
6. Run the server: ``python manage.py runserver``
7. Open website in browser at ``http://localhost:8000``


### After initial setup ###
1. Activate the virtualenv: ``source venv/bin/activate``
2. Run the server: ``python manage.py runserver``
3. Open website in browser at ``http://localhost:8000``

Dvelopment of project is supported by European Commision through the [ROUTE-TO-PA project](http://routetopa.eu/)
