from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'kids-art-show-home'),
    path('about', views.about, name = 'kids-art-show-about')
]