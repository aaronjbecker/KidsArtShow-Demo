"""
from https://github.com/jimfmunro/django-remember-me
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class AuthenticationRememberMeForm(AuthenticationForm):
    """
    Subclass of Django ``AuthenticationForm`` which adds a remember me
    checkbox.
    """
    remember_me = forms.BooleanField(label='Remember Me', initial=True,
        required=False)
