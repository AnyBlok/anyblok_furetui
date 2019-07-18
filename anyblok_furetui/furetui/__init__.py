# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok, BlokManager
from anyblok_furetui.release import version
from os.path import join
from .i18n import fr, en
from logging import getLogger

logger = getLogger(__name__)


class FuretUIBlok(Blok):
    """Setup FuretUI for AnyBlok"""
    version = version
    author = 'Suzanne Jean-Sébastien'
    logo = 'static/images/logo.png'

    required = [
        'anyblok-core',
    ]

    css = [
    ]
    js = [
        'components/about.js',
        'components/homepage.js',
        'components/app.js',
        'components/login.js',
        'components/logout.js',
    ]

    views = [
    ]
    i18n = {
        'en': en,
        'fr': fr,
    }  # key is the local
    components = [
        'components/about.tmpl',
        'components/homepage.tmpl',
        'components/app.tmpl',
        'components/login.tmpl',
        'components/logout.tmpl',
    ]

    def load(self):
        self.registry.FuretUI.pre_load()

    @classmethod
    def import_declaration_module(cls):
        from . import furetui  # noqa
        from . import menus  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import furetui
        reload(furetui)
        from . import menus
        reload(menus)

    @classmethod
    def pyramid_load_config(cls, config):
        blok_path = BlokManager.getPath('furetui')
        path = join(blok_path, 'static', 'furet-ui')
        config.add_static_view('furet-ui/js', join(path, 'js'))
        config.add_static_view('furet-ui/css', join(path, 'css'))
        config.scan(cls.__module__ + '.views')
