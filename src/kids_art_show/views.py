from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from .forms import KidsArtShowUserCreationForm
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


class UserProfile(generic.TemplateView):
    template_name = 'kids_art_show/user_profile.html'


class SignUp(generic.CreateView):
    form_class = KidsArtShowUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'kids_art_show/registration/signup.html'





# TODO: how to merge the lines below with the signup view above?
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .forms import UesrRegisterForm
#
# def register(request):
#     if request.method == 'POST':
#         form = UesrRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             messages.success(request, f'Account created for {username}!')
#             return redirect('kids-art-show-home')
#     else:
#         form = UesrRegisterForm()
#     return render(request, 'users/register.html', {'form' : form})