""" Packaging script for muse_gdrive."""
import shlex
import subprocess

import setuptools


def run(cmd):
    """ Simple helpter to run a shell command and get the output. """
    return subprocess.check_output(shlex.split(cmd)).decode('utf-8').strip()


setuptools.setup(name='muse_gdrive',
                 version=run('git describe --abbrev=0'),
                 description='Google Drive Manipulation',
                 install_requires=['click', 'google-api-python-client'],
                 packages=['muse_gdrive'],
                 scripts=['bin/google_drive'])
