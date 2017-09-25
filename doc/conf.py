""" Configuration file for Sphinx documentation generation. """
import os
import shlex
import subprocess
import sys


def run(cmd):
    """ Simple helpter to run a shell command and get the output. """
    return subprocess.check_output(shlex.split(cmd)).decode('utf-8').strip()


# If GIT_DIR is set we're in the pre-commit hook, and won't be in the directory
# with .git. Temporarily delete the GIT_DIR environment variable so we can run
# the git commands required to get the version number and then restore the
# value.
old_val = os.environ['GIT_DIR'] if 'GIT_DIR' in os.environ else None
if old_val:
    del os.environ['GIT_DIR']
version = release = run('git describe')
if old_val:
    os.environ['GIT_DIR'] = old_val

sys.path.insert(0, os.path.abspath('..'))
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.githubpages']
source_suffix = '.rst'
master_doc = 'index'
project = 'muse_gdrive'
copyright = '2017, Aaron Jones'
author = 'Aaron Jones'
language = None
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'sphinx_rtd_theme'
htmlhelp_basename = 'muse_gdrive'
