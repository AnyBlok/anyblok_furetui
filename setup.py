# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Hugo QUEZADA <gohu@hq.netlib.re>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import os
from setuptools import setup, find_packages
version = '0.0.1'

requires = [
    'anyblok',
    'anyblok_io',
    'anyblok_pyramid',
    'anyblok_pyramid_beaker',
    'anyblok_pyramid_rest_api',
    'lxml',
    'rst2html5',
    'python-magic',
    'simplejson',
    'pyjsparser',
]

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), 'r', encoding='utf-8') as readme:
    README = readme.read()

with open(
    os.path.join(here, 'doc', 'CHANGES.rst'), 'r', encoding='utf-8'
) as change:
    CHANGE = change.read()

with open(
    os.path.join(here, 'doc', 'FRONT.rst'), 'r', encoding='utf-8'
) as front:
    FRONT = front.read()

setup(
    name="anyblok_furetui",
    version=version,
    author="Jean-Sébastien Suzanne",
    author_email="jssuzanne@anybox.fr",
    description="FuretUI for AnyBlok",
    license="MPL2",
    long_description=README + '\n' + FRONT + '\n' + CHANGE,
    url="http://furetui.anyblok.org/%s" % version,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=requires,
    tests_require=requires + ['nose'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
    ],
    entry_points={
        'bloks': [
            'furetui=anyblok_furetui.furetui:FuretUIBlok',
            'furetui-auth=anyblok_furetui.auth:FuretUIAuthBlok',
        ],
    },
    extras_require={},
)
