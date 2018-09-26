from django import forms

class ArtAddFrom(forms.Form):
    title = forms.CharField()
    description = forms.CharField()