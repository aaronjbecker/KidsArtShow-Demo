"""
AJB 12/2/18: another take at testing post creation, this time
    explicitly as a test script.
    started from copy of seed_db_models.py
"""
# TODO: cleanup imports and setup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kids_art_show.settings")
# TODO: do you need the setup call in a unit test file?
import django
django.setup()
# import django components used in tests
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.shortcuts import reverse
# import aliasing to support module reloading during interactive
import kids_art_show.models as kasm
import pandas as pd


# path to excel file with tables of test data to seed database
_xl_path = "test_data_seed.xlsx"
# path to version-controlled test images
_test_img_dir = "test_images"
# account for different interactive/console contexts
wd = os.getcwd()
if "kas_test" not in wd:
    _xl_path = os.path.join(wd, "kas_test", _xl_path)
    _test_img_dir = os.path.join(wd, "kas_test", _test_img_dir)
else:
    _xl_path = os.path.join(wd, _xl_path)
    _test_img_dir = os.path.join(wd, _test_img_dir)


def read_test_users(xl_path: str = None):
    if xl_path is None:
        xl_path = _xl_path
    test_users = pd.read_excel(xl_path, sheetname="users")
    return test_users


def read_test_creators(xl_path: str = None):
    if xl_path is None:
        xl_path = _xl_path
    test_creators = pd.read_excel(xl_path, sheetname="creators")
    return test_creators


def read_test_posts(xl_path: str = None):
    if xl_path is None:
        xl_path = _xl_path
    test_posts = pd.read_excel(xl_path, sheetname="posts")
    return test_posts


def add_objects():
    # create users
    tu = read_test_users()
    for _, urow in tu.iterrows():
        # need to use create_user to get password hashed and login supported etc.
        # cf. https://stackoverflow.com/a/23482284
        kasm.KidsArtShowUser.objects.create_user(**urow.to_dict())
        pass

    # now create child artist profiles
    tc = read_test_creators()
    for _, crow in tc.iterrows():
        cdict = crow.to_dict()
        # add content creator via relation to parent account
        # cf. https://docs.djangoproject.com/en/2.1/ref/models/relations/
        p = kasm.KidsArtShowUser.objects.get(username=cdict['parent_account'])
        # remove parent account from dict and set as related item
        cdict.pop('parent_account', None)
        p.contentcreator_set.create(**cdict)
        pass


def read_image_file(image_fn: str,
                    image_dir: str = None,
                    content_type: str = 'image/jpeg'):
    """AJB 12/3/18: read an image file from specified/default directory into a Django upload container"""
    if image_dir is None:
        image_dir = _test_img_dir
    img_path = os.path.join(image_dir, image_fn)
    with open(img_path, 'rb') as img:
        # convert bytes to uploaded file so you can attach it to form as a file
        return SimpleUploadedFile(image_fn, img.read(),
                                  content_type=content_type)


class PostUploadTests(TestCase):
    def setUp(self):
        # flush database w/o prompt
        # for options cf. https://github.com/django/django/blob/master/django/core/management/commands/flush.py
        call_command('flush', interactive=False)
        # factor out the stuff that works already:
        # load users and creators into database
        add_objects()
        # use first set of credentials to log in test client
        tu = read_test_users()
        self.creds = tu.iloc[0].to_dict()
        # get creator name and post names associated with this user
        tc = read_test_creators()
        tp = read_test_posts()
        # get first artist associated with this user
        self.creator = tc.loc[tc['parent_account'] == self.creds['username']].iloc[0].to_dict()
        # get the first post by this artist
        self.post = tp.loc[tp['author'] == self.creator['profile_name']].iloc[0].to_dict()


    def tearDown(self):
        # normally delete objects, but here you want them preserved...?
        pass

    def test_uploading_image_post(self):
        myClient = Client()
        myClient.login(username=self.creds['username'], password=self.creds['password'])
        # read image from test directory as per module-level defaults above
        post_file = read_image_file(self.post['image'])
        # author is a choicefield that expects the content creator ID
        author_obj = kasm.ContentCreator.objects.get(profile_name=self.creator['profile_name'])
        author_id = author_obj.id
        form_data = {'author': str(author_id),
                     'title': self.post['title'],
                     'content': self.post['content'],
                     'image': post_file}
        response = myClient.post(reverse('create_post'), form_data, follow=True)
        # TODO: test that response resulted in successful creation of post image
        # successful post creation should return to user dashboard
        self.assertTrue('user_dashboard' in response.redirect_chain[0][0],
                        "Successful post creation should redirect to user dashboard!")
