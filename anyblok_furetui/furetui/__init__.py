# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok, BlokManager
from anyblok.config import Configuration
from anyblok_furetui.release import version
from os.path import join
from logging import getLogger
from .i18n import fr, en
from .pyramid import json_data_adapter

logger = getLogger(__name__)


def import_module(reload=None):
    from . import core
    from . import system
    from . import furetui
    from . import space
    from . import resource
    from . import menus
    from . import crud
    if reload is not None:
        reload(core)
        reload(system)
        reload(furetui)
        reload(space)
        reload(resource)
        reload(menus)
        reload(crud)


class FuretUIBlok(Blok):
    """Setup FuretUI for AnyBlok"""
    version = version
    priority = 1
    author = 'Suzanne Jean-Sébastien'
    logo = 'static/images/logo.png'

    required = [
        'anyblok-core',
        'pyramid',
    ]

    furetui = {
        'i18n': {
            'en': en,
            'fr': fr,
        },
        'templates': [
        ],
    }

    def load(self):
        self.registry.FuretUI.pre_load()
        logger.info('Preload Models.field_description')
        for Model in self.registry.loaded_namespaces.values():
            if Model.is_sql:
                Model.fields_description()

    @classmethod
    def import_declaration_module(cls):
        import_module()

    @classmethod
    def reload_declaration_module(cls, reload):
        import_module(reload=reload)

    @classmethod
    def pyramid_load_config(cls, config):
        json_data_adapter(config)
        blok_name, static_path = Configuration.get(
            'furetui_client_static', 'furetui:static').split(':')
        blok_path = BlokManager.getPath(blok_name)
        path = join(blok_path, *static_path.split('/'))
        config.add_static_view('furet-ui/js', join(path, 'js'))
        config.add_static_view('furet-ui/css', join(path, 'css'))
        config.add_static_view('/js', join(path, 'js'))
        config.add_static_view('/css', join(path, 'css'))
        config.scan(cls.__module__ + '.views')
