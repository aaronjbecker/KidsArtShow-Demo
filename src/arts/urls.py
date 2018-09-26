from django.urls import path, re_path
from .views import detail_view, list_view, detail_slug_view,create_view,update_view

urlpatterns = [
    re_path(r'detail/(?P<object_id>\d+)/$', detail_view, name = 'detail_view'),
    re_path(r'detail/(?P<object_id>\d+)/edit/$', update_view, name = 'update_view'),
    re_path(r'detail/(?P<slug>[\w-]+)/$', detail_slug_view, name = 'detail_slug_view'),
    re_path(r'list/$', list_view, name = 'list_view'),
    re_path(r'create/$', create_view, name = 'create_view')
]