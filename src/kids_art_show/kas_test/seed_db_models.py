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
import logging
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

# configure logger to display information messages to console
_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)
_log.addHandler(logging.StreamHandler())

# path to excel file with tables of test data to seed database
_xl_path = "test_data_seed.xlsx"
# path to version-controlled test images
_test_img_dir = "test_images"
# default values for database/migration clearing
_db_name = 'db.sqlite3'
_media_folder = 'media'
# amend path to account for different interactive/console contexts
wd = os.getcwd()
if "kas_test" not in wd:
    _xl_path = os.path.join(wd, "kas_test", _xl_path)
    _test_img_dir = os.path.join(wd, "kas_test", _test_img_dir)
else:
    _xl_path = os.path.join(wd, _xl_path)
    _test_img_dir = os.path.join(wd, _test_img_dir)


def read_model_wks(sheetname:str,
                   xl_path: str = None):
    """DRY refactoring"""
    if xl_path is None:
        xl_path = _xl_path
    models = pd.read_excel(xl_path, sheetname=sheetname)
    return models


def read_test_users(xl_path: str = None):
    return read_model_wks('users', xl_path)


def read_test_creators(xl_path: str = None):
    return read_model_wks('creators', xl_path)


def read_test_posts(xl_path: str = None):
    return read_model_wks('posts', xl_path)


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

# AJB 12/10/18: no followers privacy level, so remove from valid values
_privacy_mapping = {'private': 1,
                    'public': 3}


def add_objects():
    # create users
    tu = read_test_users()
    _log.info(f"adding {len(tu)} users...\n")
    # keep track of like source users
    like_sources = []
    for _, urow in tu.iterrows():
        # need to use create_user to get password hashed and login supported etc.
        # cf. https://stackoverflow.com/a/23482284
        udict = urow.to_dict()
        dp = udict.pop('default_privacy')
        # hack- manual mappign from test to db formats
        dp = _privacy_mapping[dp]
        usr = kasm.KidsArtShowUser.objects.create_user(**udict, default_privacy=dp)
        if udict['username'].startswith('likeSrc'):
            like_sources.append(usr)

    # now create child artist profiles
    tc = read_test_creators()
    _log.info(f"adding {len(tc)} children...\n")
    for _, crow in tc.iterrows():
        cdict = crow.to_dict()
        # add content creator via relation to parent account
        # cf. https://docs.djangoproject.com/en/2.1/ref/models/relations/
        p = kasm.KidsArtShowUser.objects.get(username=cdict['parent_account'])
        # remove parent account from dict and set as related item
        cdict.pop('parent_account', None)
        p.children.create(**cdict)

    # create sample posts
    tp = read_test_posts()
    _log.info(f"adding {len(tp)} posts...\n")
    # AJB 12/10/18: post data contains an extra column with n_likes, use that to seed likes
    # likes are provided by users named likeSrc1 to likeSrc20
    for _, prow in tp.iterrows():
        # pop number of likes since you have to create that by adding users
        n_likes = prow['n_likes']
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
        pst = frm.save()
        if n_likes:
            # also skip adding likes if the post has 0 likes
            for like_usr in like_sources[:n_likes]:
                pst.users_like.add(like_usr)


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
    # if path does not exist, return
    _log.info(f'deleting directory {dir}\n')
    if not os.path.exists(dir) or not os.path.isdir(dir):
        raise FileExistsError('{} does not exist!'.format(dir))
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
    try:
        nukedir(_media_folder)
    except FileExistsError:
        pass
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
