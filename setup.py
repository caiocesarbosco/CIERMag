# python
# -*- coding: utf-8 -*-

import codecs
import os
import re
from setuptools import setup


print('Starting install for Front End Non Real Time Subsystem ...')


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    # https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r').read()

long_description = read('README.rst')
requirements = read('REQUIREMENTS.rst').splitlines()
version = find_version("frontendnorts", "__init__.py")

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python']

setup(name='FENoRTS',
      version=version,
      description='Front End - Non Real Time Subsystem',
      author='Pedro Victor Souza',
      author_email='pedro.victor.souza@usp.br',
      long_description=long_description,
      packages=[],
      classifiers=classifiers,
      install_requires=requirements,

      )
