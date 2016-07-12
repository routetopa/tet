from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /search/
    url(r'^search/$', views.search, name='search'),
    # ex: /dataset/abc-123-asd/
    url(r'^dataset/(?P<dataset_id>[a-zA-Z0-9-]+)$', views.dataset, name='dataset'),
]
