"""
AJB 12/1/18: script to populate user, artist, Post, etc. w/ initial data
    to facilitate layout development and testing.
    TODO: Nuke entire database and re-build migrations before seeding data
    loading methodology as per https://stackoverflow.com/a/18760222
    TODO: consider making a manage.py command,
        cf. https://timonweb.com/posts/how-to-run-an-arbitrary-script-in-the-context-of-the-django-project/
"""
# TODO: cleanup imports and setup
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
import glob
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kids_art_show.settings")
# set up django env so you can use models, etc.
import django
django.setup()
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

_privacy_mapping = {'private': 1,
                    'public': 3,
                    'followers': 2}


def add_objects():
    # create users
    tu = read_test_users()
    for _, urow in tu.iterrows():
        # need to use create_user to get password hashed and login supported etc.
        # cf. https://stackoverflow.com/a/23482284
        kasm.KidsArtShowUser.objects.create_user(**urow.to_dict())

    # now create child artist profiles
    tc = read_test_creators()
    for _, crow in tc.iterrows():
        cdict = crow.to_dict()
        # add content creator via relation to parent account
        # cf. https://docs.djangoproject.com/en/2.1/ref/models/relations/
        p = kasm.KidsArtShowUser.objects.get(username=cdict['parent_account'])
        # remove parent account from dict and set as related item
        cdict.pop('parent_account', None)
        dp = cdict.pop('default_privacy')
        # hack- manual mappign from test to db formats
        dp = _privacy_mapping[dp]
        p.children.create(**cdict, default_privacy=dp)


    # create sample posts
    tp = read_test_posts()
    for _, prow in tp.iterrows():
        # add post by creating and saving ModelForm
        # get creator object and associated parent user
        c = kasm.ContentCreator.objects.get(profile_name=prow['author'])
        parent = c.parent_account
        # load specified image into upload container
        post_img = read_image_file(prow['image'])
        frm_data = {'author': str(c.pk),
                    'title': prow['title'],
                    'description': prow['description'],
                    'privacy_level': _privacy_mapping[prow['privacy']]}
        # TODO: load privacy
        frm_files = {'image': post_img}
        frm = kasf.CreatePostForm(frm_data, frm_files, user=parent)
        frm.save()


def navigate_to_root(root_dir: str = 'src'):
    # navigate up directories until you find specified root directory
    # TODO: what happens if you can't find root?
    while True:
        # will always be a directory
        wd = os.getcwd()
        # get final folder part of path
        curr_folder = os.path.basename(os.path.normpath(wd))
        if curr_folder == root_dir:
            break
        else:
            # move up one level
            os.chdir('..')


def nukedir(dir):
    """cf. https://stackoverflow.com/a/13766571"""
    if dir[-1] == os.sep: dir = dir[:-1]
    files = os.listdir(dir)
    for file in files:
        if file == '.' or file == '..': continue
        path = dir + os.sep + file
        if os.path.isdir(path):
            nukedir(path)
        else:
            os.unlink(path)
    os.rmdir(dir)


# default values for database/migration clearing
_db_name = 'db.sqlite3'
_media_folder = 'media'


def completely_clear_db():
    """AJB 12/3/18: delete database and all migrations, then re-run migrations.
        Designed to provide a complete reset prior to seeding the database."""
    # TODO: refactor into separate script and call from shell for windows
    # note: Windows users may see permission errors.
    # assumes you start in project root directory
    # cf. https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html
    # find all migrations using unix-style glob syntax
    res = glob.glob("*/migrations/*.py", recursive=True)
    # also delete compiled/cached migrations, but use 1 loop
    res += glob.glob("*/migrations/*.pyc", recursive=True)
    for f in res:
        if f.endswith('__init__.py'):
            # don't delete init from migrations
            continue
        os.remove(f)
    # nuke and recreate media folder where images are stored server-side
    nukedir(_media_folder)
    os.mkdir(_media_folder)
    # now delete the database itself
    os.remove(_db_name)


if __name__ == '__main__':
    # save initial working directory
    init_wd = os.getcwd()
    # navigate to root directory
    navigate_to_root()
    # clear pre-existing database contents
    completely_clear_db()
    # remake migrations (on top of empty db) and build db
    call_command('makemigrations', interactive=False)
    call_command('migrate', interactive=False)

    # now re-insert objects from the pre-defined test data
    add_objects()
