from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils.text import slugify

# Create your models here.

class Art(models.Model):
    title = models.CharField(max_length=30)
    slug = models.SlugField(blank=True)
    description = models.TextField(null=True)
    category = models.CharField(max_length=20,null=True)

    def __str__(self):
        return self.title

def art_pre_save_reciever(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)

pre_save.connect(art_pre_save_reciever, sender=Art)

# def art_post_save_reciever(sender, instance, *args, **kwargs):
#     if instance.slug !=slugify(instance.title):
#         instance.slug = slugify(instance.title)
#
# post_save.connect(art_post_save_reciever, sender=Art)