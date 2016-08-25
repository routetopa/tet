from django.conf.urls import url

from . import views

# urlpatterns = [
#     url(r'^(?P<filename>(robots.txt)|(humans.txt))$', name='home-files'),
# ]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /search/
    url(r'^search/$', views.search, name='search'),
    # ex: /dataset/abc-123-id/
    url(r'^dataset/(?P<dataset_id>[a-zA-Z0-9-]+)$', views.dataset, name='dataset'),
    # ex: /dataset/abc-123-id/app
    url(r'^dataset/(?P<dataset_id>[a-zA-Z0-9-]+)/app$', views.dataset_as_app, name='dataset_as_app'),
    # ex: /dataset/abc-123-id/pdf
    url(r'^dataset/(?P<dataset_id>[a-zA-Z0-9-]+)/pdf$', views.dataset_as_pdf, name='dataset_as_pdf'),
    # ex: /dataset/abc-123-id/table
    url(r'^dataset/(?P<dataset_id>[a-zA-Z0-9-]+)/table$', views.dataset_as_table, name='dataset_as_table'),
        # ex: /dataset/abc-123-id/table
    url(r'^api/table/(?P<resource_id>[a-zA-Z0-9-]+)/(?P<field_id>[\w|\W]+)$', views.table_api, name='table_api'),

]

