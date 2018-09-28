from django.urls import path, re_path
# from .views import detail_view, list_view, detail_slug_view,create_view,update_view
from .views import (
    ArtListView,
    ArtDetailView,
    ArtCreateView,
    ArtUpdateView
    )

app_name = 'arts'  # app_name for name space new in django 2.0
urlpatterns = [
    # re_path(r'^detail/(?P<object_id>\d+)/$', detail_view, name = 'detail_view'),
    # re_path(r'^detail/(?P<slug>[\w-]+)/$', detail_slug_view, name = 'detail_slug_view'),
    # re_path(r'^list/$', list_view, name = 'list_view'),
    # re_path(r'^detail/(?P<object_id>\d+)/edit/$', update_view, name = 'update_view'),
    # re_path(r'^create/$', create_view, name = 'create_view')
    re_path(r'^$', ArtListView.as_view(), name = 'list'),
    re_path(r'^add/$', ArtCreateView.as_view(), name = 'create'),
    re_path(r'^(?P<pk>\d+)/$', ArtDetailView.as_view(), name='detail'),
    re_path(r'^(?P<slug>[\w-]+)/$', ArtDetailView.as_view(), name = 'detail_slug'),
    re_path(r'^(?P<pk>\d+)/edit/$', ArtUpdateView.as_view(), name = 'update'),
    re_path(r'^(?P<slug>[\w-]+)/edit/$', ArtUpdateView.as_view(), name = 'update_slug'),
]