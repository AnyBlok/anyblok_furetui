# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#    Copyright (C) 2020 Pierre Verkest <pierreverkest84@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok_io.blok import BlokImporter
from anyblok_furetui.release import version
from anyblok_pyramid import PERM_WRITE, merge


def import_module(reload=None):
    from . import user
    if reload is not None:
        reload(user)


class FuretUIAuthBlok(Blok, BlokImporter):
    version = version
    author = 'Suzanne Jean-Sébastien'
    logo = 'static/images/logo.png'

    required = [
        'anyblok-core',
        'pyramid',
        'furetui',
        'anyblok-io-xml',
        'auth',
        'auth-password',
        'authorization',
    ]

    furetui = {
        'templates': [
            'templates/user.tmpl',
            'templates/role.tmpl',
        ],
    }

    @classmethod
    def import_declaration_module(cls):
        import_module()

    @classmethod
    def reload_declaration_module(cls, reload):
        import_module(reload=reload)

    def update(self, latest):
        self.import_file_xml('Model.FuretUI.Space', 'data', 'spaces.xml')
        self.import_file_xml('Model.FuretUI.Resource', 'data', 'resources.xml')
        self.import_file_xml('Model.FuretUI.Menu', 'data', 'menus.xml')
        self.update_admin_role()

    def update_admin_role(self):
        self.anyblok.Pyramid.Role.ensure_exists(
            "admin",
            [
                {
                    "code": "role-admin-pyramid-authorization",
                    "model": "Model.Pyramid.Authorization",
                    "perms": PERM_WRITE,
                },
                {
                    "code": "role-admin-pyramid-role",
                    "model": "Model.Pyramid.Role",
                    "perms": PERM_WRITE,
                },
                {
                    "code": "role-admin-pyramid-user",
                    "model": "Model.Pyramid.User",
                    "perms": PERM_WRITE,
                },
                {
                    "code": "role-admin-system-blok",
                    "model": "Model.System.Blok",
                    "perms": merge(PERM_WRITE, {'admin': {'matched': True}}),
                },
            ],
            label="Administrator"
        )
