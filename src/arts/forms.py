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

class ArtModelForm(forms.ModelForm):
    # adds new fields in regular django form, if there are same fields from model, it over-rides it
    category = forms.ChoiceField(choices = CATEGORY_CHOICES)
    # add fields coming from model
    class Meta:
        model = Art
        fields = [
            'title',
            'category',
            'description',
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
