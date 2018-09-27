from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit  import CreateView, UpdateView

from .forms import ArtAddForm, ArtModelForm
from .models import Art
from .mixins import MultiSlugMixin, SubmitBtnMixin
# Create your views here.

class ArtCreateView(SubmitBtnMixin,CreateView):
    model = Art
    template_name = 'form.html'
    form_class = ArtModelForm
    success_url = '/arts/add'
    submit_btn = 'Create Art'

class ArtUpdateView(SubmitBtnMixin,MultiSlugMixin,UpdateView):
    model = Art
    template_name = 'form.html'
    form_class = ArtModelForm
    success_url = '/arts/list/'
    submit_btn = 'Add Art'

    def get_object(self, *args, **kwargs):
        obj = super(ArtUpdateView,self).get_object(*args,**kwargs)
        user = self.request.user
        if obj.user == user or user in obj.managers.all():
            return obj
        else:
            raise Http404

class ArtListView(ListView):
    model = Art
    def get_queryset(self, *args, **kwargs):
        qs = super(ArtListView,self).get_queryset(**kwargs)
        return qs

class ArtDetailView(MultiSlugMixin,DetailView):
    model = Art




# =======================
def update_view(request,object_id):
    art = get_object_or_404(Art,id = object_id)
    form = ArtModelForm(request.POST or None, instance=art)
    if form.is_valid():
        instance = form.save(commit = False)
        instance.save()
    template = 'form.html'
    context = {
        'art': art,
        'form':form,
        'submit_btn':'Update Art'
    }
    return render(request, template, context)

def create_view(request):
    print(request.POST)
    form = ArtModelForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit = False)
        instance.save()
    # form = ArtAddForm(request.POST or None)
    # if request.method == 'POST':
    #     print(request.POST.get('title'))
    # if form.is_valid():
    #     data = form.cleaned_data
    #     title = data.get('title')
    #     description = data.get('description')
    #     category = data.get('category')
    #     new_obj = Art()
    #     new_obj.title = title
    #     new_obj.description = description
    #     new_obj.category = category

        # print(request.POST.get('title'))
    template = 'form.html'
    context = {
        'form': form,
        'submit_btn': 'Create Art'
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
    queryset = Art.objects.all()
    template = 'list_view.html'
    context = {
        'queryset': queryset
    }
    return render(request, template, context)

#=========================================================

