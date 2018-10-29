"""
AJB 10/28/18: adapted from https://wsvincent.com/django-custom-user-model-tutorial/
"""
# Register your admin models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import KidsArtShowUserCreationForm, KidsArtShowUserChangeForm
from .models import KidsArtShowUser

class KidsArtShowAdmin(UserAdmin):
    add_form = KidsArtShowUserCreationForm
    form = KidsArtShowUserChangeForm
    model = KidsArtShowUser
    list_display = ['email', 'username', 'birth_date', 'bio']

admin.site.register(KidsArtShowUser, KidsArtShowAdmin)
