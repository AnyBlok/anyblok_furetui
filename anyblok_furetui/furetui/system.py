# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from ..security import exposed_method


@Declarations.register(Declarations.Model.System)
class Blok:

    @exposed_method(is_classmethod=False, permission='admin')
    def install(self):
        super(Blok, self).install()
        # MAIBE reload UI

    @exposed_method(is_classmethod=False, permission='admin')
    def uninstall(self):
        super(Blok, self).uninstall()
        # MAIBE reload UI

    @exposed_method(is_classmethod=False, permission='admin')
    def upgrade(self):
        super(Blok, self).uninstall()
        # MAIBE reload UI
