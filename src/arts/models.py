from django.urls import reverse
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils.text import slugify

# Create your models here.

def download_file_location(instance,filename):
    return'{}/{}'.format(instance.id,filename)

class Art(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=True)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='art_managers')
    title = models.CharField(max_length=30)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField(null=True)
    category = models.CharField(max_length=20,null=True)
    file = models.FileField(blank=True, null=True, upload_to=download_file_location)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        view_name = 'arts:detail_slug'
        return reverse(view_name,kwargs={'slug':self.slug})

    def get_update_url(self):
        view_name = 'arts:update_slug'
        return reverse(view_name,kwargs={'slug':self.slug})

def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Art.objects.filter(slug = slug)
    exists = qs.exists()
    if exists:
        new_slug = "{}-{}".format(slug,qs.first().id)
        return create_slug(instance, new_slug = new_slug)
    return slug


def art_pre_save_reciever(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(art_pre_save_reciever, sender=Art)

# def art_post_save_reciever(sender, instance, *args, **kwargs):
#     if instance.slug !=slugify(instance.title):
#         instance.slug = slugify(instance.title)
#
# post_save.connect(art_post_save_reciever, sender=Art)