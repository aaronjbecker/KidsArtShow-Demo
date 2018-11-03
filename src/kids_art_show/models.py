"""
Aaron J Becker 10/28/18: define model classes, starting with user data.
cf. https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#substituting-a-custom-user-model

TODO: define requirements for intended user types and associated classes
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class KidsArtShowUser(AbstractUser):
    """
    User class that handles authentication on the KAS website.
    Will also contain additional "user profile" properties.
    """
    # TODO: define a more appropriate set of fields
    bio = models.TextField(max_length=500)
    child_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class ContentCreator(models.Model):
    profile_name = models.CharField(max_length=100)
    parent_account = models.ForeignKey(KidsArtShowUser,
                                       on_delete=models.CASCADE)
    # TODO: other child-related fields, e.g. bio, age, favorite color, etc.
    
    def __str__(self):
        return self.profile_name


class Post(models.Model):
    """
    Posts are associated with KidsArtShowUser classes
    """
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(KidsArtShowUser,
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.title
