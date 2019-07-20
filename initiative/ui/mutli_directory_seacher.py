import os
import re
from cached_property import cached_property


class File(object):

    def __init__(self, full_path, root):
        self.full_path = full_path
        self.root = root

    @cached_property
    def display_name(self):
        return os.path.relpath(self.full_path, self.root)

    @cached_property
    def sort_name(self):
        return os.path.basename(self.full_path)

    def __str__(self):
        return self.display_name


class MultiDirectorySearcher(object):

    DEFAULT_REGEX = re.compile(r'.*')

    def __init__(self):
        self._directories = None
        self._files = []
        self.reset_regex()

    def reset_regex(self):
        self._regex = self.DEFAULT_REGEX

    def set_directories(self, *directories):
        self._directories = directories
        self._files = self.walk_fs()

    def refresh(self):
        self._files = self.walk_fs()

    def walk_fs(self):
        objs = []
        for directory in self._directories:
            objs.extend(self._walk_directory(directory))
        return objs

    def _walk_directory(self, directory):
        objs = []
        for root, _, files in os.walk(directory):
            for file in files:
                if self.considered_file(file):
                    full_path = os.path.join(root, file)
                    objs.append(File(full_path, directory))
        return objs

    def considered_file(self, filename):
        raise NotImplementedError

    def set_regex(self, value):
        self._regex = re.compile(value)

    def get_files(self):
        files = [file for file in self._files if self._regex.search(file.display_name)]
        return sorted(files, key=lambda x: x.sort_name)
