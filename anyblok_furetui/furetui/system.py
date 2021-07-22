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
    def furetui_install(self):
        self.anyblok.upgrade(install=(self.name,))
        return [{'type': 'RELOAD'}]

    @exposed_method(is_classmethod=False, permission='admin')
    def furetui_uninstall(self):
        self.anyblok.upgrade(uninstall=(self.name,))
        return [{'type': 'RELOAD'}]

    @exposed_method(is_classmethod=False, permission='admin')
    def furetui_update(self):
        self.anyblok.upgrade(update=(self.name,))
        return [{'type': 'RELOAD'}]
