.. This file is a part of the AnyBlok project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. image:: https://img.shields.io/pypi/v/anyblok_furetui.svg
   :target: https://pypi.python.org/pypi/anyblok_furetui/
   :alt: Version status

.. image:: https://travis-ci.org/AnyBlok/anyblok_furetui.svg?branch=master
    :target: https://travis-ci.org/AnyBlok/anyblok_furetui
    :alt: Build status

.. image:: https://coveralls.io/repos/github/AnyBlok/anyblok_furetui/badge.svg?branch=master
    :target: https://coveralls.io/github/AnyBlok/anyblok_furetui?branch=master
    :alt: Coverage

.. image:: https://readthedocs.org/projects/anyblok_furetui/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://doc.anyblok.org/en/latest/?badge=latest

.. image:: https://badges.gitter.im/AnyBlok/community.svg
    :alt: gitter
    :target: https://gitter.im/AnyBlok/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge

.. image:: https://img.shields.io/pypi/pyversions/anyblok_furetui.svg?longCache=True
    :alt: Python versions

AnyBlok FuretUI
===============

|furetui|

FuretUI is a web client for AnyBlok.

AnyBlok FuretUI is the glue between AnyBlok and FuretUI that expose your model
as CRUD, implement required furetui HTTP interfaces which helps developer
to make suite user interfaces to AnyBlok projects.

+-----------------------+--------------------+-------------------------------------------------+
| Blok                  | Dependencies       | Description                                     |
+=======================+====================+=================================================+
| **furetui**           |  **pyramid**       | Main blok to define UI for anyblok              |
|                       |  **anyblok-io**    |                                                 |
+-----------------------+--------------------+-------------------------------------------------+
| **furetui-auth**      | **furetui**        | add authentication and  authorisation of        |
|                       | **anyblok-io-xml** | **Anyblok-Pyramid**                             |
|                       | **auth**           |                                                 |
|                       | **auth-password**  |                                                 |
|                       | **authorization**  |                                                 |
+-----------------------+--------------------+-------------------------------------------------+
| **furetui-address**   | **furetui**        | Use authorisation of anyblok-pyramid            |
|                       | **address**        |                                                 |
+-----------------------+--------------------+-------------------------------------------------+
| **furetui-delivery**  | **furetui**        | Use delivery of anyblok-delivery                |
|                       | **delivery**       |                                                 |
+-----------------------+--------------------+-------------------------------------------------+
| **furetui-filter-ip** | **furetui**        | Filter ip on pyramid api for furetui            |
+-----------------------+--------------------+-------------------------------------------------+

Installation
------------

Install released versions of AnyBlok from the Python package index with
`pip <http://pypi.python.org/pypi/pip>`_ or a similar tool::

    pip install anyblok_furetui

Installation via source distribution is via the ``setup.py`` script::

    python setup.py install

Installation will add the ``anyblok``, ``anyblok-pyramid`` commands to the environment.

Running Tests
-------------

To run framework tests with ``pytest``::

    pip install pytest
    ANYBLOK_DATABASE_DRIVER=postgresql ANYBLOK_DATABASE_NAME=test_anyblok py.test anyblok_furetui/tests

To run tests of all installed bloks with demo data::

    anyblok_createdb --db-name test_anyblok --db-driver-name postgresql --install-bloks --with-demo furetui-auth furetui-filter-ip
    ANYBLOK_DATABASE_DRIVER=postgresql ANYBLOK_DATABASE_NAME=test_anyblok py.test anyblok_furetui/furetui anyblok_furetui/ip anyblok_furetui/auth

AnyBlok is tested continuously using `Travis CI
<https://travis-ci.org/AnyBlok/anyblok_furetui>`_

Contributing (hackers needed!)
------------------------------

AnyBlok is ready for production usage even though it can be
improved and enriched.
Feel free to fork, talk with core dev, and spread the word !

Author
------

Jean-Sébastien Suzanne

Contributors
------------

* Jean-Sébastien Suzanne
* Pierre Verkest
* Hugo Quezada

Bugs
----

Bugs and features enhancements to AnyBlok should be reported on the `Issue
tracker <http://issue.anyblok.org>`_.

anyblok_furetui is released under the terms of the `Mozilla Public License`.

See the `latest documentation <http://furetui.anyblok.org/>`_

.. |furetui| image:: anyblok_furetui/furetui/static/images/logo.png
