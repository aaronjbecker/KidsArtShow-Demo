from django.shortcuts import render
from django.http import HttpResponse
from . import views
from .models import Post

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'kids_art_show/home.html', context)

def about(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'kids_art_show/about.html', context)