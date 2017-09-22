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


class LowLevelBlok(Blok):
    version = version
    author = 'Suzanne Jean-Sébastien'
    logo = '../logo.png'

    required = [
        'furetui',
    ]

    views = [
        'db.tmpl',
    ]

    def update(self, latest_version):
        """ Update the database """
        self.import_file('xml', 'Model.Web.Action', 'action.xml')
        self.import_file('xml', 'Model.Web.Space', 'space.xml')

    def uninstall(self):
        Mapping = self.registry.IO.Mapping
        Mapping.delete_for_blokname(self.name, byquery=True)
        Mapping.clean(bloknames=[self.name])
        self.registry.expire_all()
