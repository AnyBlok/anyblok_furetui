# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok_furetui.release import version
from logging import getLogger

logger = getLogger(__name__)


def import_module(reload=None):
    logger.info('Import module reload=%r', True if reload else False)
    from . import furetui
    if reload is not None:
        reload(furetui)


class FuretUIFilterIPBlok(Blok):
    """Setup FuretUI for AnyBlok"""
    version = version
    author = 'Suzanne Jean-Sébastien'
    logo = 'static/images/logo.png'

    required = [
        'anyblok-core',
        'pyramid',
        'furetui',
    ]

    def load(self):
        self.registry.FuretUI.define_authorized_ips()

    @classmethod
    def import_declaration_module(cls):
        import_module()

    @classmethod
    def reload_declaration_module(cls, reload):
        import_module(reload=reload)
