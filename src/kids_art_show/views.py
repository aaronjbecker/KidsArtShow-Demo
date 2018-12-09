import re
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, reverse, resolve_url
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.forms import formset_factory
import kids_art_show.forms as kasf
from .forms import KidsArtShowUserCreationForm, ManageChildrenFormset, CreatePostForm, ManageChildrenFormsetHelper
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
    # generate the URL from reverse so you know your redirect will be valid
    login_redirect = reverse('process_login', args=[request.path])
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
def edit_art(request, slug):
    # use existing create post form, but populate with initial data?
    art = get_object_or_404(Post, slug=slug)
    # form action returns to this view on submit for processing
    form_action = reverse('edit_art', args=[slug])
    if request.method == "GET":
        # no changed data to validate
        form = kasf.EditArtForm(instance=art, form_action=form_action)
    else:
        # TODO: incorporate valid changes
        clear_img = 'image-clear' in request.POST and request.POST['image-clear'] == 'on'
        # if you want to clear the image, pop the image key from POST so the form validates
        # the field can't be empty, but it can be missing (weird)
        # QueryDict is immutable and returns a list for each element, when you just want the raw value
        # post_data = dict(request.POST.dict)
        post_data = request.POST.dict()
        # hack: ignore errors on image file input if you're clearing the image
        form = kasf.EditArtForm(post_data, request.FILES, form_action=form_action)
        form.full_clean()
        if clear_img:
            form.errors.pop('image', None)
        # TODO: test form with errors
        if not form.errors:
        # if form.is_valid():
            # cleaned data is valid, but how do you check for cleared image?
            cd = form.cleaned_data
            # if you didn't want to clear the image and the image is None, pop that key
            if not clear_img and 'image' in cd and not cd['image']:
                cd.pop('image')
            elif clear_img:
                # explicitly clear the image if that's what user wanted to do
                cd['image'] = None
            for fld, val in cd.items():
                setattr(art, fld, val)
            art.save()
            # TODO: redirect to success url on save of valid data
            # will call get_absolute_url on model object
            return redirect(art)
    # return new form, or form with errors
    return render(request, 'kids_art_show/edit_art.html', {'edit_form': form,
                                                           'art': art})


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
def process_inline_login(request, src=None):
    """
    Explicitly designed to be called only from inline navbar login form
    src must be a valid URL recognized by django
    """
    form = rmf.RembmerMeAuthFormInline(data=request.POST)
    # store post data, force clean in view if present in request.session when view is loaded
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
        # have to force serialization, cf. https://stackoverflow.com/a/19734757
        form_data = {str(k):str(v) for k, v in form.data.items() if str(k) != 'csrfmiddlewaretoken'}
    # use session to store form data; this is imperfect but should suffice for basic stuff here
    # cf. https://stackoverflow.com/a/9000663
    request.session['login_data'] = form_data
    # resolve URL using any available patterns
    return redirect(resolve_url(src))


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
    # for now, just public
    arts = Post.public_posts.all()
    if request.user.is_authenticated:
        # use user's queryset/manager to get related entitled posts
        # use OR to merge querysets, cf. https://simpleisbetterthancomplex.com/tips/2016/06/20/django-tip-5-how-to-merge-querysets.html
        arts = arts | Post.owned_posts(request.user)
    # return public posts
    ctx = {'arts': arts,
           'login_form': login_form}
    return render(request, 'kids_art_show/list.html', context=ctx)


def art_detail(request, slug):
    # get login form to use in navigation bar
    login_form = get_login_form(request)
    # TODO: permission checking of some sort
    art = get_object_or_404(Post, slug=slug)
    is_owner = False
    if request.user.is_authenticated:
        owner = art.author.parent_account
        is_owner = owner.pk == request.user.pk
    return render(request,
                  'kids_art_show/art_detail.html',
                  {'art': art,
                   'login_form': login_form,
                   'is_owner': is_owner})


def about(request):
    # get login form to use in navigation bar
    login_form = get_login_form(request)
    context = {
        'login_form': login_form,
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


@login_required
def manage_artists(request):
    template_name = 'kids_art_show/manage_formset.html'
    heading_message = "Manage Artist Profiles"
    formset = None
    # create formatting helper
    helper = kasf.ManageChildrenFormsetHelper()
    if request.method == 'GET':
        # initially, populate forms with this user's children
        formset = ManageChildrenFormset(queryset=request.user.children.all())
    elif request.method == 'POST':
        formset = ManageChildrenFormset(request.POST)
        if formset.is_valid():
            for form in formset:
                cd = form.cleaned_data
                if 'id' in cd and cd['id']:
                    # extract int from ModelFormset object
                    cd['id'] = cd['id'].id
                if cd.get('profile_name', False):
                    # parent account is user logged into this form
                    cd['parent_account_id'] = request.user.id
                    # django automatically knows to execute an update or an insert
                    ContentCreator(**cd).save()
            return redirect('user_dashboard')
    return render(request, template_name,
                  { 'formset': formset,
                    'helper': helper,
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
