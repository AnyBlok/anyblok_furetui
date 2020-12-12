# This file is a part of the AnyBlok / FuretUI project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration
from .release import version


Configuration.add_application_properties(
    'furetui-user', ['logging', 'furetui_user'],
    prog='Add user or update password, version %r' % version,
    description="User manager",
)


@Configuration.add('furetui_user', label="User management for FuretUI")
def define_wsgi_option(group):
    group.add_argument('--furetui-user-login')
    group.add_argument('--furetui-user-password')
    group.add_argument('--furetui-user-roles', nargs="+")
