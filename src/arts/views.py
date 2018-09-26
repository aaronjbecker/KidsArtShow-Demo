from django.http import Http404
from django.shortcuts import render, get_object_or_404

from .forms import ArtAddFrom
from .models import Art
# Create your views here.

def create_view(request):
    print(request.POST)
    form = ArtAddFrom()
    template = 'create_view.html'
    context = {
        'form': form,
    }
    return render(request, template, context)

def detail_slug_view(request, slug = None):
    try:
        art = get_object_or_404(Art,slug = slug)
    except Art.MultipleObjectsReturned:
        art = Art.objects.filter(slug = slug).order_by('title').first()
    template = 'detail_view.html'
    context = {
        'art': art
    }
    return render(request, template, context)

def detail_view(request, object_id = None):
    art = get_object_or_404(Art,id = object_id)
    template = 'detail_view.html'
    context = {
        'art': art
    }
    return render(request, template, context)

def list_view(request):
    print(request)
    template = 'list_view.html'
    context = {}
    return render(request, template, context)