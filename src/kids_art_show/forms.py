"""
AJB 10/28/18: Basic user creation and change forms.
Adapted from https://wsvincent.com/django-custom-user-model-tutorial/
"""
from django.shortcuts import reverse
from django.forms import ModelForm, modelformset_factory
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import KidsArtShowUser, ContentCreator, Post
from django.contrib.auth.decorators import login_required
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.bootstrap import StrictButton
from django.forms.models import ModelChoiceField


class KidsArtShowUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = KidsArtShowUser
        fields = ('username', 'email', 'birth_date')


class KidsArtShowUserChangeForm(UserChangeForm):

    class Meta:
        model = KidsArtShowUser
        fields = ('username', 'email', 'birth_date')


class CreatePostForm(ModelForm):
    # TODO: form helper with layout, submit button, etc.
    # note need for class to enable image upload (TODO: lookup)
    class Meta:
        model = Post
        fields = ('title', 'author', 'content', 'image')

    def __init__(self, *args, form_action:str = None, **kwargs):
        if form_action is None:
            # TODO: is this the right way to do this?
            form_action = reverse("create_post")
        # author = None
        # if 'author' in kwargs:
        #     author = kwargs.pop('author')
        # user is used to select ContentCreators, not fed to superclass ctor
        self.user = kwargs.pop('user')
        super(CreatePostForm, self).__init__(*args, **kwargs)
        # problem is that queryset is not evaluated until form is rendered...
        qs = ContentCreator.objects.filter(parent_account=self.user.id)
        mcf = ModelChoiceField(qs)
        self.fields['author'] = mcf
        # force full clean after specifying valid author choices
        self.full_clean()
        # create form helper to assist with crispy forms formatting
        self.helper = FormHelper(self)
        self.helper.form_action = form_action
        self.helper.layout = Layout('title', 'author', 'content', 'image',
            StrictButton('Login', css_class='btn-default', type='submit'))

# class ManageChildForm(ModelForm):
#     """form for a parent/authentication account to manage child profiles"""
#     class Meta:
#         model = ContentCreator
#         fields = ['profile_name', 'nickname']
#         labels = {'profile_name': 'Artist Profile Name'}


ManageChildrenFormset = \
    modelformset_factory(ContentCreator,
                         fields=['profile_name', 'nickname'],
                         min_num=1)

