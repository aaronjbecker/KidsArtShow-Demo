"""
AJB 12/2/18: another take at testing post creation, this time
    explicitly as a test script.
    started from copy of seed_db_models.py
"""
# TODO: cleanup imports and setup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kids_art_show.settings")

from PIL import Image
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.utils.six import BytesIO

# import model classes
import django
django.setup()
# from kids_art_show.models import KidsArtShowUser
# import aliasing to support module reloading during interactive
import kids_art_show.models as kasm
import kids_art_show.forms as kasf
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


# "borrowed" from easy_thumbnails/tests/test_processors.py
# cf. http://blog.cynthiakiser.com/blog/2016/06/26/testing-file-uploads-in-django/
def create_image(storage, filename, size=(100, 100),
                 image_mode='RGB', image_format='JPG'):
    """
    Generate a test image, returning the filename that it was saved as.

    If ``storage`` is ``None``, the BytesIO containing the image data
    will be passed instead.
    """
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    if not storage:
        return data
    image_file = ContentFile(data.read())
    return storage.save(filename, image_file)


class PostUploadTests(TestCase):
    def setUp(self):
        # flush database w/o prompt
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
        self.creator = tc.loc[tc['parent_account'] == self.creds['username']].iloc[0].to_dict()
        self.post = tp.loc[tp['author'] == self.creator['profile_name']].iloc[0].to_dict()
        # provide full path to image
        self.post['image'] = os.path.join(_test_img_dir, self.post['image'])


    def tearDown(self):
        # normally delete objects, but here you want them preserved...?
        pass

    def test_uploading_image_post(self):
        myClient = Client()
        myClient.login(username=self.creds['username'], password=self.creds['password'])




if __name__ == '__main__':
    put = PostUploadTests()
    put.run()
    pass
    # # factor out the stuff that works already
    # add_objects()
    # # get use and use first set of credentials to log in test client
    # tu = read_test_users()
    # creds = tu.iloc[0]
    # # _, creds = next(tu.iterrows())
    #
    #
    # # finally, create some sample posts
    # tp = read_test_posts()
    # for _, postRow in tp.iterrows():
    #     pdict = postRow.to_dict()
    #     # add post via relation to creator
    #     c = kasm.ContentCreator.objects.get(profile_name=pdict['author'])
    #     pdict.pop('author', None)
    #     # add path to image
    #     pdict['image'] = os.path.join(_test_img_dir, pdict['image'])
    #     # img = pdict.pop('image')
    #     # uses related_name attribute
    #     # frm = kasf.CreatePostForm(data=pdict, files=[img])
    #
    #     c.artist.create(**pdict)
    #     pass
