#!/usr/bin/env python3

import address_book
from distutils.core import setup

data_files = [('share/applications/', ['data/addressbook.desktop']),
              ('share/icons/', ['data/addressbook.jpeg'])]

setup(
    name = 'addressbook',
    packages = ['address_book', 'address_book/resources'],
    scripts = ['addressbook'],
    data_files = data_files,
    version = address_book.__version__,
    description = 'GUI application to organize your contacts',
    author = 'Ilias Stamatis',
    author_email = 'stamatis.iliass@gmail.com',
    license = 'GNU GPL3',
    platforms = 'Platform Independent',
    url = 'https://github.com/Ilias95/Address-Book',
    keywords = ['addressbook', 'contacts'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Natural Language :: English',
        'Intended Audience :: End Users/Desktop'],
    long_description = """
Address Book
-------------

Address Book is a simple, GUI, platform independent, multi-user application
which helps you to organize your contacts.

Requires: python3, PyQt4
"""
)
