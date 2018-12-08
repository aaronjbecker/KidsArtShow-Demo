"""
AJB 10/28/18: adapted from https://wsvincent.com/django-custom-user-model-tutorial/
# Register your admin models here.
"""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import KidsArtShowUserCreationForm, KidsArtShowUserChangeForm
from .models import KidsArtShowUser, Post


class KidsArtShowAdmin(UserAdmin):
    """
    This class determines the fields that appear in the user administration view
    """
    add_form = KidsArtShowUserCreationForm
    form = KidsArtShowUserChangeForm
    model = KidsArtShowUser
    # TODO: better list of fields to display for user admin?
    # list_display = ['email', 'username', 'birth_date', 'bio']

# TODO: create post administration view?

# register admin objects and/or model classes
admin.site.register(KidsArtShowUser, KidsArtShowAdmin)

# admin.site.register(Post)
# register admin view for Post with customized settings
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'image', 'date_posted', 'slug']
    list_filter = ['date_posted']

