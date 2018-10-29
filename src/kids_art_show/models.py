"""
Aaron J Becker 10/28/18: define model classes, starting with user data.
cf. https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#substituting-a-custom-user-model

TODO: define requirements for intended user types and associated classes
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class KidsArtShowUser(AbstractUser):
    """
    User class that handles authentication on the KAS website.
    Will also contain additional "user profile" properties.
    """
    # TODO: define a more appropriate set of fields
    bio = models.TextField(max_length=500)
    child_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)

