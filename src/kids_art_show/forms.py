"""
AJB 10/28/18: Basic user creation and change forms.
Adapted from https://wsvincent.com/django-custom-user-model-tutorial/
"""
# TODO: cleanup imports
from django.shortcuts import reverse
import django.forms as djf
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
import kids_art_show.models as kasm
from .models import KidsArtShowUser, ContentCreator, Post
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.bootstrap import StrictButton
from django.forms.models import ModelChoiceField
# import crispy_forms.layout as cfl
from crispy_forms.layout import Submit, HTML
from django.forms.widgets import ClearableFileInput, CheckboxInput
from django.utils.html import mark_safe, conditional_escape, escape


class KidsArtShowUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = KidsArtShowUser
        fields = ('username', 'email', 'birth_date')


class KidsArtShowUserChangeForm(UserChangeForm):

    class Meta:
        model = KidsArtShowUser
        fields = ('username', 'email', 'birth_date')


class CreatePostForm(djf.ModelForm):

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


class ArtInput(ClearableFileInput):
    """renders the input file as an avatar image, and removes the 'currently' html
        take 2: override template, more contemporary version.
        cf. https://stackoverflow.com/a/52901700 """
    clear_checkbox_label = 'Remove Saved Art?'
    template_name = 'kids_art_show/art_input_widget.html'


class EditArtForm(djf.ModelForm):
    """needs to allow changes without submitting a new image file...
        overrides default fields with non-required values and prevents changes to fields that aren't editable. """

    # fields not listed here will not be editable
    title =  djf.CharField(required=True)
    # note: label is handled by customized widget template
    image = djf.ImageField(required=False, widget=ArtInput, label='')
    # note that text fields differ from char fields only in their input widget, and don't have a separate class
    description = djf.CharField(required=False, widget=djf.Textarea)
    privacy_level = djf.ChoiceField(choices=kasm.PRIVACY_CHOICES, required=True)

    class Meta:
        model = Post
        fields = ('title', 'description', 'image', 'privacy_level')

    def __init__(self, *args, form_action:str = None, **kwargs):
        if form_action is None:
            # pass completed form back to create post view for processing/possible redirect
            form_action = reverse("edit_art")
        # user is used to select ContentCreators, not fed to superclass ctor
        super(EditArtForm, self).__init__(*args, **kwargs)
        # force full clean after specifying valid author choices
        self.full_clean()
        # create form helper to assist with crispy forms formatting
        self.helper = FormHelper(self)
        self.helper.form_action = form_action
        self.helper.layout = Layout('title', 'privacy_level', 'description', 'image',
                                    StrictButton('Update Your Art!', css_class='btn-default', type='submit'))



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
    djf.modelformset_factory(ContentCreator,
                         fields=('profile_name', 'nickname', 'bio'),
                         min_num=1)

