"""
Aaron J Becker 10/28/18: define model classes, starting with user data.
cf. https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#substituting-a-custom-user-model

TODO: define requirements for intended user types and associated classes
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

# define a set of privacy levels applied to profiles and posts
# TODO: use some standard set of privacy levels if such a thing exists
# PRIVACY_CHOICES = [('PVT', 'Private'),
#                    ('FLW', 'Followers'),
#                    ('PUB', 'Public')]
# define privacy choices using integer field
PRIVACY_CHOICES = ((1, 'Private'),
                   (2, 'Followers'),
                   (3, 'Public'))

# create children queryset for parent account to simplify access
# class ChildrenManager(models.Manager):
#     def get_queryset(self):
#         return super(ChildrenManager,
#                      self).get_queryset() \
#             .filter(status='published')





class KidsArtShowUser(AbstractUser):
    """
    User class that handles authentication on the KAS website.
    This class can best be thought of as representing a parent/caretaker w/ one or more children.
    Will also contain additional "user profile" properties.
    """
    # TODO: define a more appropriate set of fields
    bio = models.TextField(max_length=500)
    # TODO: define method to determine whether user is old enough to create an account
    birth_date = models.DateField(null=True, blank=True)
    # TODO: method to associate parent account with one or more children; these are created after account registration.
    # TODO: method to distinguish between parent and viewer accounts
    # TODO: following

    def __str__(self):
        return self.first_name + " " + self.last_name


class ContentCreator(models.Model):
    """
    Conceptually, a "child" on the platform- a parent may manage multiple child profiles
    """
    profile_name = models.CharField(max_length=100, unique=True)
    parent_account = models.ForeignKey(KidsArtShowUser,
                                       on_delete=models.CASCADE,
                                       related_name='children')
    nickname = models.CharField(max_length=20, null=True, default=None)
    bio = models.TextField(max_length=1000, null=True, default=None)
    # TODO: what should default privacy setting be?
    default_privacy = models.IntegerField(choices=PRIVACY_CHOICES, default=1)
    # TODO: other child-related fields, e.g. bio, age, favorite color, etc.

    # TODO: manager for public profiles; should be indexed by number of followers?


    def __str__(self):
        return self.profile_name


def image_fn(instance, filename):
    """
    Creates storage path for image file associated with post.
    :param instance: post instance
    :param filename: original file name
    :return: storage path
    """
    # prepend date posted, as utc timestamp
    #   (timestamp includes seconds, to prevent errors on duplicate filename submissions)
    return "{}/{}_{}".format(instance.author.profile_name, timezone.now().timestamp(), filename)


class PublicPostManager(models.Manager):
    def get_queryset(self):
        # encoding for public posts
        return super().get_queryset().filter(privacy_level=3)


class Post(models.Model):
    """
    Posts are associated with ContentCreator instances
    They contain an image as well as optional text
    TODO: maybe more than one image?
    TODO: maybe also comments?
    """
    author = models.ForeignKey(ContentCreator, null=True,
                               related_name='artist',
                               on_delete=models.SET_NULL)
    title = models.CharField(max_length=100)
    # note: storage manager defaults to FileSystemStorage with base at MEDIA_ROOT
    image = models.ImageField(upload_to=image_fn, null=True, default=None)
    # use slugs rather than primary keys for navigation, for security purposes
    slug = models.SlugField(max_length=200, blank=True)
    # TODO: make description a markdown field?
    description = models.TextField(null=True, default=None)
    # automatically use current time at creation; create an index in database for posting date.
    date_posted = models.DateTimeField(auto_now_add=True,
                                       db_index=True)
    # TODO: privacy level field, categorical
    privacy_level = models.IntegerField(choices=PRIVACY_CHOICES, default=1)
    # track which users have liked an image so that you don't allow duplicate likes
    users_like = models.ManyToManyField(KidsArtShowUser,
                                        related_name='posts_liked',
                                        blank=True)
    # still want default manager available
    objects = models.Manager()
    public_posts = PublicPostManager()

    # use both post date and title when generating slug
    def save(self, *args, **kwargs):
        # if not self.privacy_level:
        #     self.privacy_level = self.author.default_privacy
        if not self.slug:
            slug_basis = "{}_{}_{}".format(timezone.now().strftime('%y%m%d_%H%M%s'), self.author, self.title)
            self.slug = slugify(slug_basis)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author} on {self.date_posted}"

    def get_absolute_url(self):
        return reverse('detail', args=[self.slug])