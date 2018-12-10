"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = "kids_art_show"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.art_feed, name = 'feed'),
    path('feed', views.art_feed, name='feed'),
    path('feed/<str:sort_by>', views.art_feed, name='feed'),
    path('signup', views.signup, name='signup'),
    path('login',
         views.process_remember_me_login,
         name='login'),
    path('process_login/<path:src>', views.process_inline_login, name='process_login'),
    path('user_dashboard', views.user_dashboard, name='user_dashboard'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('manage_artists', views.manage_artists, name='manage_artists'),
    path('create_post', views.create_post, name='create_post'),
    path('detail/<slug:slug>/', views.art_detail, name='detail'),
    path('edit_art/<slug:slug>', views.edit_art, name='edit_art'),
    path('like', views.art_like, name='like'),
    path('account_settings', views.user_settings, name='account_settings')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
