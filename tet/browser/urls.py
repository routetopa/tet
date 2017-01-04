from django.conf.urls import url
from django.conf.urls import include
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
    url(r'^dataset/(?P<dataset_id>[a-zA-Z0-9-]+)/summary$', views.dataset_as_summary, name='dataset_as_summary'),
        # ex: /dataset/abc-123-id/table
    url(r'^api/table/(?P<resource_id>[a-zA-Z0-9-]+)/(?P<field_id>[\w|\W]+)$', views.table_api, name='table_api'),
    url(r'^api/query/(?P<query>[\w|\W]+)/(?P<field_id>[\w|\W]+)$', views.query_api, name='query_api'),
    url(r'^api/graph/(?P<resource_id>[a-zA-Z0-9-]+)$', views.box_plot, name='graph_api'),
    url(r'^api/graph/(?P<resource_id>[a-zA-Z0-9-]+)/corr$', views.corr_mat, name='corr_graph_api'),
    url(r'^api/text/(?P<dataset_id>[a-zA-Z0-9-]+)/(?P<info_type>[\w|\W]+)$', views.text_api, name='text_api'),
    url(r'^api/typeahead$', views.typeahead, name='typeahead'),
    url(r'^api/cards$', views.cards, name='cards'),
    url(r'^combine$', views.combine, name='combine'),
    url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),

]

