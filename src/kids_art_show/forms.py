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
from crispy_forms.layout import Submit

class KidsArtShowUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = KidsArtShowUser
        fields = ('username', 'email', 'birth_date')


class KidsArtShowUserChangeForm(UserChangeForm):

    class Meta:
        model = KidsArtShowUser
        fields = ('username', 'email', 'birth_date')


class CreatePostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'author', 'description', 'image', 'privacy_level')

    def __init__(self, *args, form_action:str = None, **kwargs):
        if form_action is None:
            # pass completed form back to create post view for processing/possible redirect
            form_action = reverse("create_post")
        # user is used to select ContentCreators, not fed to superclass ctor
        user = kwargs.pop('user')
        super(CreatePostForm, self).__init__(*args, **kwargs)
        # these intermediate assignments do help with forcing evaluation,
        #   at least while debugging (in practice)
        qs = user.children.all()
        mcf = ModelChoiceField(queryset=qs)
        self.fields['author'] = mcf
        # set initial privacy to user's default privacy
        self.fields['privacy_level'].initial = user.default_privacy
        # force full clean after specifying valid author choices
        self.full_clean()
        # create form helper to assist with crispy forms formatting
        self.helper = FormHelper(self)
        self.helper.form_action = form_action
        self.helper.layout = Layout('title', 'author', 'description', 'image', 'privacy_level',
            StrictButton('Post Your Art!', css_class='btn-default', type='submit'))



class EditArtForm(ModelForm):
    """needs to allow changes without submitting a new image file..."""
    class Meta:
        model = Post
        fields = ('title', 'author', 'description', 'image', 'privacy_level')

    def __init__(self, *args, form_action:str = None, **kwargs):
        if form_action is None:
            # pass completed form back to create post view for processing/possible redirect
            form_action = reverse("create_post")
        # user is used to select ContentCreators, not fed to superclass ctor
        user = kwargs.pop('user')
        super(EditArtForm, self).__init__(*args, **kwargs)
        # these intermediate assignments do help with forcing evaluation,
        #   at least while debugging (in practice)
        qs = user.children.all()
        mcf = ModelChoiceField(queryset=qs)
        self.fields['author'] = mcf
        # set initial privacy to user's default privacy
        self.fields['privacy_level'].initial = user.default_privacy
        # force full clean after specifying valid author choices
        self.full_clean()
        # create form helper to assist with crispy forms formatting
        self.helper = FormHelper(self)
        self.helper.form_action = form_action
        self.helper.layout = Layout('title', 'author', 'description', 'image', 'privacy_level',
            StrictButton('Post Your Art!', css_class='btn-default', type='submit'))



class ManageChildrenFormsetHelper(FormHelper):
    def __init__(self, *args, form_action='manage_artists', **kwargs):
        super(ManageChildrenFormsetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout('profile_name', 'nickname', 'bio',
                             StrictButton('Update Children', css_class='btn-default', type='submit'))
        self.template = 'bootstrap/table_inline_formset.html'
        self.add_input(Submit('submit', 'Save Artist Profiles'))
        self.form_action = form_action
        self.render_required_fields = True


# class ManageChildrenFormset(ModelFormset):


ManageChildrenFormset = \
    modelformset_factory(ContentCreator,
                         fields=('profile_name', 'nickname', 'bio'),
                         min_num=1)

