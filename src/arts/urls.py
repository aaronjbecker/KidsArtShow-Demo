from django.urls import path, re_path
from .views import detail_view, list_view, detail_slug_view,create_view,update_view
from .views import (
    ArtListView,
    ArtDetailView,
    ArtCreateView,
    ArtUpdateView
    )

urlpatterns = [
    # re_path(r'^detail/(?P<object_id>\d+)/$', detail_view, name = 'detail_view'),
    # re_path(r'^detail/(?P<slug>[\w-]+)/$', detail_slug_view, name = 'detail_slug_view'),
    # re_path(r'^list/$', list_view, name = 'list_view'),
    # re_path(r'^detail/(?P<object_id>\d+)/edit/$', update_view, name = 'update_view'),
    # re_path(r'^create/$', create_view, name = 'create_view')
    re_path(r'^list/$', ArtListView.as_view(), name = 'art_list_view'),
    re_path(r'^detail/(?P<pk>\d+)/$', ArtDetailView.as_view(), name='art_detail_view'),
    re_path(r'^detail/(?P<slug>[\w-]+)/$', ArtDetailView.as_view(), name = 'art_detail_slug_view'),
    re_path(r'^detail/(?P<pk>\d+)/edit/$', ArtUpdateView.as_view(), name = 'art_update_view'),
    re_path(r'^add/$', ArtCreateView.as_view(), name = 'art_create_view')
]