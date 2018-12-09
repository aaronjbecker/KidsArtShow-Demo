"""
from https://github.com/jimfmunro/django-remember-me
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import HTML, Div


class RembmerMeAuthFormInline(AuthenticationForm):
    """includes styling for inline/horizontal layout
        many options are hard-coded for use with Kids_Art_Show """

    remember_me = forms.BooleanField(label='Remember Me', initial=True,
                                     required=False)

    def __init__(self, *args, form_action="process_login", **kwargs):
        super(RembmerMeAuthFormInline, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-inline'
        self.helper.form_action = form_action
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'username',
            'password',
            'remember_me',
            StrictButton('Login', css_class='btn-default', type='submit'),
        )




class AuthenticationRememberMeForm(AuthenticationForm):
    """
    Subclass of Django ``AuthenticationForm`` which adds a remember me
    checkbox.
    """

    def __init__(self, *args, form_action="login", **kwargs):
        super(AuthenticationRememberMeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div('username', 'password',
                'remember_me', css_class='container-fluid'),
            StrictButton('Login', css_class='btn-default', type='submit'),
        )

    remember_me = forms.BooleanField(label='Remember Me', initial=True,
        required=False)
