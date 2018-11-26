from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.forms import formset_factory
from .forms import KidsArtShowUserCreationForm, ManageChildrenFormset
from .models import Post, ContentCreator


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


class UserDashboard(generic.TemplateView):
    template_name = "kids_art_show/user_dashboard.html"


class SignUp(generic.CreateView):
    form_class = KidsArtShowUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'kids_art_show/registration/signup.html'


# TODO: attempt to use a FormSet/ModelFormSet to allow editing more than one child profile?
def manage_artists(request):
    template_name = 'kids_art_show/manage_formset.html'
    heading_message = "Manage Artist Profiles"
    formset = None
    if request.method == 'GET':
        formset = ManageChildrenFormset(queryset=ContentCreator.objects.none())
    elif request.method == 'POST':
        formset = ManageChildrenFormset(request.POST)
        if formset.is_valid():
            for form in formset:
                cd = form.cleaned_data
                if cd.get('profile_name', False):
                    ContentCreator(**cd).save()
                # name = form.cleaned_data.get('name')
                # save book instance
                # if name:
                #     Book(name=name).save()
            return redirect('user_dashboard')
    return render(request, template_name,
                  { 'formset': formset,
                    'heading': heading_message })


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