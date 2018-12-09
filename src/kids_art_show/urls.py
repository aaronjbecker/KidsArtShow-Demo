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
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views
from remember_me.views import remember_me_login

app_name = "kids_art_show"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name = 'home'),
    path('/', views.home, name = 'home'),
    path('home', views.home, name='home'),
    path('about', views.about, name = 'about'),
    path('signup', views.SignUp.as_view(), name='signup'),
    # use remember-me form in helper app but with registration template defined here
    path('login',
         remember_me_login,
         kwargs = {'template_name': "kids_art_show/registration/login.html"},
         name='login'),
    # re_path(r'^process_login(/(?P<src>.*)/)?$',
    #         views.process_inline_login,
    #         name="process_login"),
    path('process_login/<path:src>', views.process_inline_login, name='process_login'),
    # TODO: profile with user ID as argument
    # TODO: user dashboard
    path('user_profile', views.UserProfile.as_view(), name='user_profile'),
    path('user_dashboard', views.UserDashboard.as_view(), name='user_dashboard'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('manage_artists', views.manage_artists, name='manage_artists'),
    path('create_post', views.create_post, name='create_post'),
    path('feed', views.art_feed, name='feed'),
    path('detail/<slug:slug>/', views.art_detail, name='detail'),
    path('like/', views.art_like, name='like'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
