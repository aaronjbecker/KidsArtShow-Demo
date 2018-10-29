from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from .forms import KidsArtShowUserCreationForm


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

class SignUp(generic.CreateView):
    form_class = KidsArtShowUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

