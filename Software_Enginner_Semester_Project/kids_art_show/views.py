from django.shortcuts import render
from django.http import HttpResponse
from . import views
from .models import Post
from django.contrib.auth.decorators import login_required

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

@login_required
def users(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'kids_art_show/users.html', context)