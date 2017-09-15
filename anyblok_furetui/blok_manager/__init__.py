# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok_furetui.release import version
from logging import getLogger
logger = getLogger(__name__)


class BlokManager(Blok):
    version = version

    required = [
        'furetui',
    ]

    views = [
        'blok.tmpl',
    ]

    @classmethod
    def import_declaration_module(cls):
        from . import blok  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import blok
        reload(blok)

    def update(self, latest_version):
        """ Update the database """
        self.import_file('xml', 'Model.Web.Space', 'space.xml')

    def uninstall(self):
        self.registry.IO.Mapping.multi_delete(
            'Model.Web.Space', 'setting_space_blok', mapping_only=False)
        self.registry.IO.Mapping.multi_delete(
            'Model.Web.Action', 'action_setting_blok', mapping_only=False)
        self.registry.expire_all()
