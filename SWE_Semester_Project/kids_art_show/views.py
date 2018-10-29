from django.shortcuts import render
from django.http import HttpResponse
from . import views

def home(request):
    return render(request, 'kids_art_show/home.html')

def about(request):
    return render(request, 'kids_art_show/about.html')