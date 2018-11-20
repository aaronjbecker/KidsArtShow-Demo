from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UesrRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        # When form.save() is going to save in this users model
        model = User
        fields = ['username', 'email', 'password1', 'password2']