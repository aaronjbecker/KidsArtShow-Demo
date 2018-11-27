"""
AJB 10/28/18: Basic user creation and change forms.
Adapted from https://wsvincent.com/django-custom-user-model-tutorial/
"""
from django.forms import ModelForm, modelformset_factory
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import KidsArtShowUser, ContentCreator
from django.contrib.auth.decorators import login_required


class KidsArtShowUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = KidsArtShowUser
        fields = ('username', 'email', 'birth_date')


class KidsArtShowUserChangeForm(UserChangeForm):

    class Meta:
        model = KidsArtShowUser
        fields = ('username', 'email', 'birth_date')


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

