import re
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.forms import formset_factory
from .forms import KidsArtShowUserCreationForm, ManageChildrenFormset
from .models import Post, ContentCreator
# import remember_me.views as rmv
import remember_me.forms as rmf
import django.contrib.auth as dca


def home(request):
    # provide instance of login form for use in navbar quick link
    # login_form = rmv.remember_me_login(request)
    login_form = rmf.RembmerMeAuthFormInline(request)
    context = {
        'login_form': login_form,
        'posts': Post.objects.all()
    }
    return render(request, 'kids_art_show/home.html', context)


@csrf_protect
@never_cache
def process_remember_me_login(request,
                              redirect_field_name='next'):
    """
    Only designed to be called from home page
    :param request:
    :param redirect_field_name:
    :param form_ctx_fld:
    :return:
    """
    # TODO: error handling if called with GET
    form = rmf.RembmerMeAuthFormInline(data=request.POST)
    redirect_to = request.POST.get(redirect_field_name, '')
    # TODO: also check for None?
    if not redirect_to:
        redirect_to = reverse_lazy('home')
    # Light security check -- make sure redirect_to isn't garbage.
    if not redirect_to or ' ' in redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL
    # Heavier security check -- redirects to http://example.com should
    # not be allowed, but things like /view/?param=http://example.com
    # should be allowed. This regex checks if there is a '//' *before* a
    # question mark.
    elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
        redirect_to = settings.LOGIN_REDIRECT_URL
    if form.is_valid():
        if not form.cleaned_data.get('remember_me'):
            request.session.set_expiry(0)

        # Okay, security checks complete. Log the user in.
        dca.login(request, form.get_user())

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

    return redirect(redirect_to, request)


def about(request):
    # provide instance of login form for use in navbar quick link
    login_form = rmf.RembmerMeAuthFormInline(request)
    context = {
        'login_form': login_form,
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

