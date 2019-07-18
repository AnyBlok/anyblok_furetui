# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok_io.blok import BlokImporter
from anyblok_furetui.release import version
from .i18n import en, fr
from logging import getLogger

logger = getLogger(__name__)


class FuretUIAuthBlok(BlokImporter, Blok):
    """Setup FuretUI for AnyBlok"""
    version = version
    author = 'Suzanne Jean-Sébastien'
    logo = 'static/images/logo.png'

    required = [
        'anyblok-core',
        'anyblok-io-xml',
        'auth',
        'furetui',
    ]

    js = [
         'components/login.js',
         'components/logout.js',
    ]
    i18n = {
        'en': en,
        'fr': fr,
    }  # key is the local
    components = [
         'components/login.tmpl',
    ]

    @classmethod
    def pyramid_load_config(cls, config):
        config.scan(cls.__module__ + '.views')

    @classmethod
    def import_declaration_module(cls):
        from . import furetui  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import furetui
        reload(furetui)

    def update(self, latest_version):
        self.import_file_xml('Model.FuretUI.Menu.User', 'menus.xml')
