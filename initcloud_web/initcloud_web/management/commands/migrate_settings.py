# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import print_function

import imp
import os
import shutil
import sys
import warnings
import json

from django.core.management.templates import BaseCommand  # noqa

# Suppress DeprecationWarnings which clutter the output to the point of
# rendering it unreadable.
warnings.simplefilter('ignore')


def get_module_path(module_name):
    """Gets the module path without importing anything.

    Avoids conflicts with package dependencies.
    (taken from http://github.com/sitkatech/pypatch)
    """
    path = sys.path
    for name in module_name.split('.'):
        file_pointer, path, desc = imp.find_module(name, path)
        path = [path, ]
        if file_pointer is not None:
            file_pointer.close()

    return path[0]


class DirContext(object):
    """Change directory in a context manager.

    This allows changing directory and to always fall back to the previous
    directory whatever happens during execution.

    Usage::

        with DirContext('/home/foo') as dircontext:
            # Some code happening in '/home/foo'
        # We are back to the previous directory.

    """

    def __init__(self, dirname):
        self.prevdir = os.path.abspath(os.curdir)
        os.chdir(dirname)
        self.curdir = os.path.abspath(os.curdir)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.prevdir)

    def __str__(self):
        return self.curdir


class Command(BaseCommand):
    help = "Creates a local_settings.py file from the default_settings.py."
    time_fmt = '%Y-%m-%d %H:%M:%S %Z'
    file_time_fmt = '%Y%m%d%H%M%S%Z'
    default_settings_file = 'default_settings.py'
    local_settings_file = 'local_settings.py'
    setting_history_file = "history.json"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        settings_file = os.path.abspath(
            get_module_path(os.environ['DJANGO_SETTINGS_MODULE'])
        )

        self.local_settings_dir = os.path.abspath(
            os.path.join(
                os.path.realpath(os.path.dirname(settings_file)),
                'local'
            )
        )

    def load_history(self):

        if not os.path.exists(self.setting_history_file):
            content = []
        else:
            with open(self.setting_history_file, 'r') as f:
                content = f.read()

            try:
                content = json.loads(content)
            except ValueError:
                content = []

        return content

    def save_history(self, history):
        with open(self.setting_history_file, 'w') as f:
            content = json.dumps(history)
            f.write(content)

    def compare_history(self, default_settings):

        default_settings_set = set(dir(default_settings))
        history = set(self.load_history())

        diff_set = default_settings_set - history
        diff_set = [name for name in diff_set if name.isupper()]

        if not diff_set:
            return

        print("Warning! new settings:")
        for name in diff_set:
            print(name)

        self.save_history(list(default_settings_set))

    def compare_settings(self, default_settings, local_settings):

        diff_set = []

        for name in dir(default_settings):

            if not name.isupper():
                continue

            default_value = getattr(default_settings, name)
            real_value = getattr(local_settings, name, default_value)

            if default_value != real_value:
                diff_set.append(name)

        if not diff_set:
            print("Dashboard now use default settings, "
                  "you may need to modify local_settings.py to suit your case")
            return

        print("Different Settings: ")
        for name in diff_set:
            print(name)

    def diff_options(self):
        """List diff of configuration names between
           self.local_settings and the example file.
        """

        with DirContext(self.local_settings_dir) as dircontext:

            if not os.path.exists(self.local_settings_file):
                shutil.copyfile(self.default_settings_file,
                                self.local_settings_file)
                print("File local_settings.py is created.")

            default_settings = imp.load_source('default_settings',
                                               self.default_settings_file)

            local_settings = imp.load_source('local_settings',
                                             self.local_settings_file)

            self.compare_settings(default_settings, local_settings)
            self.compare_history(default_settings)

    def handle(self, *args, **options):
        self.diff_options()
