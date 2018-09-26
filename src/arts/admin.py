from django.contrib import admin

# Register your models here.
from .models import Art

class ArtAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'description','category']
    search_fields = ['title', 'description']
    list_filter = ['category']
    list_editable = ['category']
    class Meta:
        model = Art

admin.site.register(Art, ArtAdmin)