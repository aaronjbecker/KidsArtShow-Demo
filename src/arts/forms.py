from django import forms
from django.forms import ModelForm

from .models import Art

CATEGORY_CHOICES = (
    ('drawings',"Drawings"),
    ('paintings',"Paintings"),
    ('ceramics','Ceramics'),
    ('collage' ,'Collage'),
    ('sculpture',"Sculpture")
)
class ArtAddForm(forms.Form):
    title = forms.CharField(label='Art Title',widget=forms.TextInput(
        attrs={
            'class':'custom-class',
            'placeholder':'Title'
    }))
    description = forms.CharField(widget=forms.Textarea(
        attrs={
            'class':'my-custom-class',
            'placeholder':'Description'
        }
    ))
    category = forms.ChoiceField(choices = CATEGORY_CHOICES)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) <= 3:
            raise forms.ValidationError('Tile must be at least 3 characters or longer')
        else:
            return title


class ArtModelForm(forms.ModelForm):
    # adds new fields in regular django form, if there are same fields from model, it over-rides it
    category = forms.ChoiceField(choices = CATEGORY_CHOICES)
    # add fields coming from model
    class Meta:
        model = Art
        fields = [
            'user',
            'title',
            'description',
            'category',
            'file'

        ]
        widgets = {
            forms.Textarea(
                attrs={
                    'class': 'my-custom-class',
                    'placeholder': 'Description'
                }
            )
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) <= 3:
            raise forms.ValidationError('Tile must be at least 3 characters or longer')
        else:
            return title
