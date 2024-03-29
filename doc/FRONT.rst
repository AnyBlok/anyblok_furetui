.. This file is a part of the AnyBlok project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..    Copyright (C) 2021 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. AnyBlok documentation master file, created by
   sphinx-quickstart on Mon Feb 24 10:12:33 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. contents::

Front Matter
============

Information about the AnyBlok / FuretUI project.

Project Homepage
----------------

AnyBlok / FuretUI is hosted on `github <http://github.com>`_ - the main project
page is at http://github.com/AnyBlok/anyblok_furetui. Source code is tracked here
using `GIT <https://git-scm.com>`_.

Releases and project status are available on Pypi at 
http://pypi.python.org/pypi/anyblok_furetui.

The most recent published version of this documentation should be at
http://furetui.anyblok.org.

Project Status
--------------

AnyBlok / FuretUI is currently in alpha status and is expected to be fairly
stable.   Users should take care to report bugs and missing features on an as-needed
basis.  It should be expected that the development version may be required
for proper implementation of recently repaired issues in between releases;
the latest master is always available at https://github.com/AnyBlok/anyblok_furetui/archive/master.zip.

Installation
------------

Install released versions of AnyBlok from the Python package index with 
`pip <http://pypi.python.org/pypi/pip>`_ or a similar tool::

    pip install anyblok_furetui

Installation via source distribution is via the ``setup.py`` script::

    python setup.py install

Installation will add the ``anyblok`` commands to the environment.

Unit Test
---------

To run framework tests with ``pytest``::

    pip install pytest
    ANYBLOK_DATABASE_DRIVER=postgresql ANYBLOK_DATABASE_NAME=test_anyblok py.test anyblok_furetui/tests

To run tests of all installed bloks with demo data::

    anyblok_createdb --db-name test_anyblok --db-driver-name postgresql --install-bloks --with-demo furetui-auth furetui-filter-ip
    ANYBLOK_DATABASE_DRIVER=postgresql ANYBLOK_DATABASE_NAME=test_anyblok py.test anyblok_furetui/furetui anyblok_furetui/ip anyblok_furetui/auth

AnyBlok / FuretUIis tested using `Travis <https://travis-ci.org/AnyBlok/anyblok_furetui>`_


Contributing (hackers needed!)
------------------------------

Anyblok / FuretUI is at a very early stage, feel free to fork, talk with core dev, and spread the word!

Author
------

* Jean-Sébastien Suzanne
* Pierre Verkest
* Hugo Quezada

Contributors
------------

`Anybox <http://anybox.fr>`_ team:

* Jean-Sébastien Suzanne

Bugs
----

Bugs and feature enhancements to AnyBlok should be reported on the `Issue 
tracker <https://bitbucket.org/AnyBlok/anyblok_furetui/issues>`_.
