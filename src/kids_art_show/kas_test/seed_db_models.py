"""
AJB 12/1/18: script to populate user, artist, Post, etc. w/ initial data
    to facilitate layout development and testing.
    loading methodology as per https://stackoverflow.com/a/18760222
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kids_art_show.settings")
# import model classes
import kids_art_show.models as kasm
import pandas as pd

# path to excel file with tables of test data to seed database
_xl_path = "test_data_seed.xlsx"
# account for different interactive/console contexts
if "kas_test" not in os.getcwd():
    _xl_path = os.path.join("kas_test", _xl_path)

_test_users = {'first_name', 'last_name', 'birth_date', 'is_staff', 'is_superuser', 'username', 'password'}

def read_test_users(xl_path: str = None):
    if xl_path is None:
        xl_path = _xl_path
    test_users = pd.read_excel(xl_path, sheetname="users")
    return test_users

if __name__ == '__main__':
    # create users

    u = kasm.KidsArtShowUser()
    u.is_superuser = True

