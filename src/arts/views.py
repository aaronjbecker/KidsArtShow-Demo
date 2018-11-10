from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse

from .forms import ArtModelForm
from .models import Art
from .mixins import MultiSlugMixin, SubmitBtnMixin,LoginRequiredMixin
# Create your views here.

class ArtCreateView(SubmitBtnMixin,CreateView):
    model = Art
    template_name = 'artsform.html'
    form_class = ArtModelForm
    # success_url = '/arts/add'
    submit_btn = 'Add Art'

    def form_valid(self,form):
        user = self.request.user
        form.instance.user = user
        valid_data = super(ArtCreateView,self).form_valid(form)
        form.instance.managers.add(user)
        return valid_data

    def get_suscess_url(self):
        return reverse('arts:list')

class ArtUpdateView(SubmitBtnMixin,MultiSlugMixin,UpdateView):
    model = Art
    template_name = 'artsform.html'
    form_class = ArtModelForm
    # success_url = '/arts/list/'
    submit_btn = 'Update Art'

    def get_object(self, *args, **kwargs):
        obj = super(ArtUpdateView,self).get_object(*args,**kwargs)
        user = self.request.user
        if obj.user == user or user in obj.managers.all():
            return obj
        else:
            raise Http404

    def get_suscess_url(self):
        return reverse('arts:list')

class ArtListView(ListView):
    model = Art
    def get_queryset(self, *args, **kwargs):
        qs = super(ArtListView,self).get_queryset(**kwargs)
        return qs

class ArtDetailView(MultiSlugMixin,DetailView):
    model = Art

def home(request):
    return render(request, 'home.html')

def users(request):
    return render(request, 'users.html')