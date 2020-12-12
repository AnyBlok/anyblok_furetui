# This file is a part of the AnyBlok / Pyramid project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import anyblok
from anyblok.config import Configuration
from logging import getLogger

logger = getLogger(__name__)


def furetui_user():
    """Update an existing database"""
    registry = anyblok.start(
        'furetui-user', loadwithoutmigration=True)
    login = Configuration.get('furetui_user_login')
    password = Configuration.get('furetui_user_password')
    roles = Configuration.get('furetui_user_roles') or []
    registry.FuretUI.user_management(login, password, roles)
