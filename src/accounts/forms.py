from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class loginForm(forms.Form):
    username = forms.CharField()
    # email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class registerForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username {} already exists'.format(username))
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email {} already exists'.format(email))
        return email

    def clean(self):
        clean_data = super(registerForm,self).clean()
        password = clean_data.get('password')
        password2 = clean_data.get('password2')

        if password != password2:
            self._errors['password'] = self.error_class(['Passwords do not match'])
            raise forms.ValidationError('Passwords do not match')
            del clean_data['password']
            del clean_data['password2']
        return clean_data

