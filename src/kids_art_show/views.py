import re
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.forms import formset_factory
from .forms import KidsArtShowUserCreationForm, ManageChildrenFormset, CreatePostForm
from .models import Post, ContentCreator
# import remember_me.views as rmv
import remember_me.forms as rmf
import django.contrib.auth as dca
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required


def get_login_form(request):
    """helper to build login form with error messages and redirects for pages that have one"""
    # provides instance of login form for use in navbar quick link
    # note that url already includes backslash
    login_redirect = "process_login{}/".format(request.path)
    login_data = {}
    # use post data, or session, or nothing
    if request.POST:
        login_data = request.POST
    else:
        if 'login_data' in request.session.keys():
            login_data = request.session['login_data']
    login_form = rmf.RembmerMeAuthFormInline(data=login_data,
                                             form_action=login_redirect)
    # if you had a non-empty dict, check for errors
    if login_data:
        login_form.full_clean()
    return login_form


def home(request):
    """render the home page"""
    # use helper above to get login_form
    login_form = get_login_form(request)
    context = {
        'login_form': login_form,
        'posts': Post.objects.all()
    }
    return render(request, 'kids_art_show/home.html', context)


@login_required
def create_post(request):
    """author is limited to user-managed artists in CreatePostForm ctor"""
    if request.method == "GET":
        # create empty form
        form = CreatePostForm(user=request.user)
    else:
        form = CreatePostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('user_dashboard'))
    # TODO: why TemplateResponse instead of render?
    return TemplateResponse(request, 'kids_art_show/create_post.html',
                            {'user': request.user, 'create_form': form})

# TODO: re_path on inline login, pass environment variable to form action (request.url)

@csrf_protect
@never_cache
@require_POST
def process_inline_login(request, src):
    """
    Explicitly designed to be called only from inline navbar login form
    src must be a valid URL recognized by django
    :param request:
    :param redirect_field_name:
    :param form_ctx_fld:
    :return:
    """
    form = rmf.RembmerMeAuthFormInline(data=request.POST)
    # context = {
    #     'login_form': form,
    #     'posts': Post.objects.all()
    # }
    # store post data, force clean in view if present on session
    form_data = {}
    if form.is_valid():
        if not form.cleaned_data.get('remember_me'):
            request.session.set_expiry(0)

        # Okay, security checks complete. Log the user in.
        dca.login(request, form.get_user())

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
    else:
        # only record data if there was an error, so the form can validate and show errors on redirect
        # TODO: this is probably insecure for some reason?
        form_data = {str(k):str(v) for k, v in form.data.items() if str(k) != 'csrfmiddlewaretoken'}
        # error_messages = dict(form.error_messages)
    # return render(request, 'kids_art_show/home.html', context)
    # use session to store form errors; this is imperfect but should suffice for basic stuff here
    # cf. https://stackoverflow.com/a/9000663
    # have to force serialization, cf. https://stackoverflow.com/a/19734757
    # request.session['login_data'] = {str(k):str(v) for k, v in error_messages.items()}
    request.session['login_data'] = form_data
    return redirect(reverse(src))


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


def art_feed(request):
    """displays feed of artworks that user is allowed to see, or only public art if not authenticated."""
    # get login form to use in navigation bar
    login_form = get_login_form(request)

    if request.user.is_authenticated:
        # use user's queryset/manager to get related entitled posts
        pass
    else:
        pass
    # for now, just public
    # return public posts
    ctx = {'arts': Post.public_posts.all(),
           'login_form': login_form}
    return render(request, 'kids_art_show/list.html', context=ctx)


def art_detail(request, slug):
    # get login form to use in navigation bar
    login_form = get_login_form(request)
    # TODO: permission checking of some sort
    art = get_object_or_404(Post, slug=slug)
    return render(request,
                  'kids_art_show/art_detail.html',
                  {'art': art})
    pass


def about(request):
    # get login form to use in navigation bar
    login_form = get_login_form(request)
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
@login_required
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


@ajax_required
@login_required
@require_POST
def art_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Post.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                # create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'ko'})
