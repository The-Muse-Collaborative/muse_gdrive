""" Module allowing simple manipulations of files on Google Drive. """

import io
import logging
import os
import sys
import time

import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials


# Configure logging.
LOGGER = logging.getLogger('muse_gdrive')
CONSOLE_LOGGER = logging.StreamHandler()
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z')
CONSOLE_LOGGER.setFormatter(FORMATTER)
LOGGER.addHandler(CONSOLE_LOGGER)
LOGGER.setLevel(logging.INFO)


def connect(secret_file_path, email_address):
    """Authenticates to Google Drive for a given user's email address."""
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(secret_file_path,
                                                             scopes=scopes)
    delegated_creds = creds.create_delegated(email_address)
    http = delegated_creds.authorize(httplib2.Http())
    service = apiclient.discovery.build('drive', 'v3', http=http)
    return service


def get_id_by_name(google_drive, name, parent_id):
    """Gets the ID of a file or folder contained in a given parent folder by
    name."""
    query = '"{0}" in parents and name = "{1}"'.format(parent_id, name)
    query_result = google_drive.files().list(pageSize=2,
                                             fields="files(id)",
                                             q=query).execute()
    items = query_result.get('files', [])
    if not items:
        raise RuntimeError('File not found! ' +
                           'Name({0}) ParentID({1})'.format(name, parent_id))
    elif len(items) > 1:
        raise RuntimeError('Multiple identically named files in directory! ' +
                           'Name({0}) Parent({1}) Count({2})'.format(
                               name, parent_id, len(items)))
    else:
        return items[0]['id']


def get_id_by_path(google_drive, path):
    """Gets the ID of a file or folder by its absolute path."""
    if not os.path.isabs(path):
        raise RuntimeError('Path {0} is not an absolute path!'.format(path))
    cur_id = 'root'
    for part in [x for x in path.split('/') if x]:
        cur_id = get_id_by_name(google_drive, part, cur_id)
    return cur_id


def make_directory(google_drive, path):
    """ Create a directory at the given location. """
    dir_id = get_id_by_path(google_drive, os.path.dirname(path))
    file_metadata = {'name': os.path.basename(path),
                     'parents': [dir_id],
                     'mimeType': 'application/vnd.google-apps.folder'}
    google_drive.files().create(body=file_metadata, fields='id').execute()


def upload(google_drive, source, dest):
    """Copies a file from the local filesystem to Google Drive."""
    dir_id = get_id_by_path(google_drive, os.path.dirname(dest))
    file_metadata = {'name': os.path.basename(dest),
                     'parents': [dir_id]}
    while True:
        media = apiclient.http.MediaFileUpload(source, resumable=True)
        request = google_drive.files().create(body=file_metadata,
                                              media_body=media,
                                              fields='id')
        errors = 0
        response = None
        while not response:
            try:
                status, response = request.next_chunk()
                if status:
                    LOGGER.info('Upload %d%% complete.',
                                int(status.progress() * 100))
            except apiclient.errors.HttpError as exc:
                if exc.resp.status in [404]:
                    break
                elif exc.resp.status in [500, 502, 503, 504]:
                    time.sleep(2 ** errors)
                    errors = errors + 1 if errors < 5 else 5
                    continue
                else:
                    raise
        else:
            break


def download(google_drive, source, dest):
    """Copies a file from Google Drive to the local filesystem."""
    file_id = get_id_by_path(google_drive, source)
    request = google_drive.files().get_media(fileId=file_id)
    with io.FileIO(dest, 'wb') as stream:
        downloader = apiclient.http.MediaIoBaseDownload(stream, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            LOGGER.info('Download %d%% complete.',
                        int(status.progress() * 100))


def delete(google_drive, path):
    """Deletes a file or folder (and children) on Google Drive."""
    file_id = get_id_by_path(google_drive, path)
    google_drive.files().delete(fileId=file_id).execute()


def list_files(google_drive, path):
    """Lists the contents of a folder on Google Drive."""
    parent = get_id_by_path(google_drive, path)
    page_token = None
    files = []
    while True:
        result = google_drive.files().list(q='"{0}" in parents'.format(parent),
                                           fields='nextPageToken, files(name)',
                                           pageToken=page_token).execute()
        for this_file in result.get('files', []):
            files.append(this_file.get('name'))
        page_token = result.get('nextPageToken', None)
        if not page_token:
            break
    return files
