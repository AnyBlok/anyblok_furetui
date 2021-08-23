.. This file is a part of the AnyBlok project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..    Copyright (C) 2021 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

API : Models
~~~~~~~~~~~~

**Core**

.. automodule:: anyblok_furetui.furetui.core

.. autoclass:: SqlMixin
    :members:
    :show-inheritance:
    :noindex:

.. autoclass:: SqlBase
    :members:
    :show-inheritance:
    :noindex:

.. autoclass:: SqlViewBase
    :members:
    :show-inheritance:
    :noindex:


 **CRUD**

.. automodule:: anyblok_furetui.furetui.core

.. autoanyblok-declaration:: CRUD
    :members:
    :show-inheritance:
    :noindex:

API : Pyramid view
~~~~~~~~~~~~~~~~~~

.. automodule:: anyblok_furetui.furetui.views.main

.. autofunction:: format_static
    :noindex:

.. autofunction:: get_static
    :noindex:

.. autofunction:: load_main
    :noindex:

.. automodule:: anyblok_furetui.furetui.views.required_data

.. autoclass:: InitialisationMixin
    :members:
    :noindex:
    :show-inheritance:
    :inherited-members:

.. autoclass:: DisconnectedInitialisation
    :members:
    :noindex:
    :show-inheritance:
    :inherited-members:

.. autoclass:: ConnectedInitialisation
    :members:
    :noindex:
    :show-inheritance:
    :inherited-members:
