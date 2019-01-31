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
from .template import Template
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
        'components/plop.css',
    ]
    js = [
        'components/about.js',
        'components/plop.js',
    ]

    views = [
    ]
    components = [
        'components/about.tmpl',
        'components/plop.tmpl',
    ]

    def load(self):
        from os.path import join
        tmpl_views = Template()
        tmpl_components = Template()
        js = []
        css = []
        Blok = self.registry.System.Blok
        for blok in Blok.list_by_state('installed'):
            b = BlokManager.get(blok)
            bpath = BlokManager.getPath(blok)
            if hasattr(b, 'views'):
                for template in b.views:
                    with open(join(bpath, template), 'r') as fp:
                        tmpl_views.load_file(fp)
            if hasattr(b, 'components'):
                for template in b.components:
                    with open(join(bpath, template), 'r') as fp:
                        tmpl_components.load_file(fp)
            if hasattr(b, 'js'):
                js.extend([join('furet-ui', blok, 'js', filename)
                           for filename in b.js])
            if hasattr(b, 'css'):
                css.extend([join('furet-ui', blok, 'css', filename)
                           for filename in b.css])

        tmpl_views.compile()
        self.registry.furetui_views = tmpl_views
        tmpl_components.compile()
        self.registry.furetui_components = tmpl_components
        self.registry.furetui_js = js
        self.registry.furetui_css = css

    @classmethod
    def import_declaration_module(cls):
        from . import furetui  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import furetui
        reload(furetui)

    @classmethod
    def pyramid_load_config(cls, config):
        config.scan(cls.__module__ + '.views')
