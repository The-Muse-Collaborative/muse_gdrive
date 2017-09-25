""" Unitests that test the muse_gdrive module. """
import datetime
import os
import tempfile

import muse_gdrive
import nose.tools


EMAIL = os.environ['MUSE_GDRIVE_EMAIL']


@nose.tools.raises(RuntimeError)
def test_non_absolute_path():
    """ Attempts to use a relative path when downloading a file. """
    google_drive = muse_gdrive.connect('test_secret.json', EMAIL)
    muse_gdrive.download(google_drive, 'somepath', 'somebadfile')


@nose.tools.raises(RuntimeError)
def test_download_nonexistant_file():
    """ Attempts to use a non-existant path when downloading a file. """
    google_drive = muse_gdrive.connect('test_secret.json', EMAIL)
    muse_gdrive.download(google_drive, '/somepath', 'somebadfile')


def test_good():
    """ Tests the success conditions of most functions.
    1. Creates a directory.
    2. Uploads a new file into it.
    3. Downloads that file back.
    4. Make sure the contents of the downloaded file match the uploaded file.
    5. Lists files in the directory, making sure they are correct.
    6. Deletes the file.
    7. Lists files in the directory again, making sure it is empty.
    8. Deletes the directory."""
    try:
        google_drive = muse_gdrive.connect('test_secret.json', EMAIL)
        test_file_name = 'test_temp.txt'
        gdrive_dir = '/unittest-' + datetime.datetime.now().isoformat()
        muse_gdrive.make_directory(google_drive, gdrive_dir)
        gdrive_path = os.path.join(gdrive_dir, test_file_name)
        expected_contents = 'TESTING TESTING 123'
        with open(test_file_name, 'w') as test_file:
            test_file.write(expected_contents)
        with open(test_file_name, 'r') as test_file:
            muse_gdrive.upload(google_drive, test_file.name, gdrive_path)
        with open(test_file_name, 'w') as test_file:
            muse_gdrive.download(google_drive, gdrive_path, test_file_name)
        with open(test_file_name, 'r') as test_file:
            actual_contents = test_file.read()
        assert actual_contents == expected_contents
        expected_file_list = [test_file_name]
        actual_file_list = muse_gdrive.list_files(google_drive, gdrive_dir)
        assert actual_file_list == expected_file_list
        muse_gdrive.delete(google_drive, gdrive_path)
        expected_file_list = []
        actual_file_list = muse_gdrive.list_files(google_drive, gdrive_dir)
        assert actual_file_list == expected_file_list
        muse_gdrive.delete(google_drive, gdrive_dir)
    finally:
        if os.path.exists(test_file_name):
            os.remove(test_file_name)
