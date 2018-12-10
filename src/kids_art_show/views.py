# TODO: Cleanup imports!
import django.contrib.auth as dca
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import reverse, resolve_url
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

import kids_art_show.forms as kasf
import remember_me.forms as rmf
from common.decorators import ajax_required
from .forms import KidsArtShowUserCreationForm, ManageChildrenFormset, CreatePostForm
from .models import Post, ContentCreator
from django.db.models import Count


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
        # QueryDict is immutable and returns a list for each element, when you just want the raw value, so use .dict()
        # cf. https://stackoverflow.com/a/15283515
        post_data = request.POST.dict()
        form = kasf.EditArtForm(post_data, request.FILES, form_action=form_action)
        form.full_clean()
        if clear_img:
            # hack: ignore errors on image file input if you're clearing the image
            form.errors.pop('image', None)
        # TODO: test form with errors other than missing image?
        if not form.errors:
            # cleaned data is the valid set of fields we should change
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
        form_data = {str(k): str(v) for k, v in form.data.items() if str(k) != 'csrfmiddlewaretoken'}
    # use session to store form data; this is imperfect but should suffice for basic stuff here
    # cf. https://stackoverflow.com/a/9000663
    request.session['login_data'] = form_data
    # resolve URL using any available patterns
    return redirect(resolve_url(src))


@csrf_protect
@never_cache
def process_remember_me_login(request):
    """
    Updated to reflect better understanding of how forms work
    """
    if request.method == "GET":
        # create new login form
        form = rmf.AuthenticationRememberMeForm()
    else:
        form = rmf.AuthenticationRememberMeForm(data=request.POST)
        form.full_clean()
        if form.is_valid():
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            # Okay, security checks complete. Log the user in.
            dca.login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            # redirect after successful login, assumes no args
            return redirect(settings.LOGIN_REDIRECT_URL)
    # render form into template, empty or with errors
    return render(request,
                  "kids_art_show/registration/login.html",
                  {'form': form})


@login_required
def user_settings(request):
    """
    Basic wrapper around KidsArtShowUserChangeForm
    :param request:
    :return:
    """
    if request.method == "GET":
        # create new login form
        form = kasf.KasUserUpdateForm(instance=request.user)
    else:
        # TODO: check for required/submitted fields?
        form = kasf.KasUserUpdateForm(data=request.POST or None, instance=request.user)
        form.full_clean()
        if form.is_valid():
            # update the user by saving form
            form.save()
            # redirect after successful login, assumes no args
            return redirect(reverse('user_dashboard'))
    # render form into template, empty or with errors
    return render(request,
                  "kids_art_show/registration/user_change.html",
                  {'form': form})


@login_required
def user_dashboard(request):
    """displays list of artworks, but only those that are owned by this user"""
    arts = Post.owned_posts(request.user)
    if arts:
        # get paginator
        paginator = Paginator(arts, 8)
        page = request.GET.get('page')
        try:
            arts = paginator.page(page)
        except PageNotAnInteger:
            arts = paginator.page(1)
        except EmptyPage:
            if request.is_ajax():
                # If the request is AJAX and the page is out of range
                # return an empty page
                return HttpResponse('')
            # If page is out of range deliver last page of results
            arts = paginator.page(paginator.num_pages)
    ctx = {'arts': arts}
    if request.is_ajax():
        return render(request,
                      'kids_art_show/list_ajax.html',
                      ctx)
    return render(request,
                  'kids_art_show/user_dashboard.html',
                  ctx)


def art_feed(request, sort_by=None):
    """displays feed of artworks that user is allowed to see, or only public art if not authenticated."""
    # get login form to use in navigation bar
    login_form = get_login_form(request)
    arts = Post.public_posts.all()
    if request.user.is_authenticated:
        # use user's queryset/manager to get related entitled posts
        # use OR to merge querysets, cf. https://simpleisbetterthancomplex.com/tips/2016/06/20/django-tip-5-how-to-merge-querysets.html
        owned = Post.owned_posts(request.user)
        if owned:
            arts = arts | owned
    # apply sort logic
    if sort_by:
        if sort_by == 'likes':
            # have to use custom logic for this; descending in number of likes, by date within same #
            # cf. https://stackoverflow.com/a/2454022
            arts = arts.annotate(like_count=Count('users_like')).order_by('-like_count', '-date_posted')
        else:
            # assume it's a regular field, no error checking, just ignore errors
            try:
                arts = arts.order_by(sort_by)
            except Exception as e:
                pass
    # get paginator
    paginator = Paginator(arts, 8)
    page = request.GET.get('page')
    try:
        arts = paginator.page(page)
    except PageNotAnInteger:
        arts = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # If the request is AJAX and the page is out of range
            # return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        arts = paginator.page(paginator.num_pages)
    ctx = {'arts': arts,
           'login_form': login_form}
    if request.is_ajax():
        return render(request,
                      'kids_art_show/list_ajax.html',
                      ctx)
    return render(request,
                  'kids_art_show/list.html',
                  ctx)


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


def signup(request):
    """function-based so you can automatically log user in"""
    if request.method == 'GET':
        form = KidsArtShowUserCreationForm()
    else:
        form = KidsArtShowUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = dca.authenticate(username=username, password=raw_password)
            # don't remember when processing sign up
            # log the user in securely
            dca.login(request, user)
            # assumes that redirect url takes no args
            return redirect(settings.LOGIN_REDIRECT_URL)
    # render blank form, or form with errors
    return render(request,
                  'kids_art_show/registration/signup.html',
                  {'form': form})


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
                  {'formset': formset,
                   'helper': helper,
                   'heading': heading_message})


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
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ko'})
