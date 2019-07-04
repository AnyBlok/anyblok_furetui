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
import pkg_resources
from logging import getLogger

logger = getLogger(__name__)


LOADING_CONTENT = pkg_resources.resource_filename("vuecli", "loading.gif")
VUE_PATH = pkg_resources.resource_filename("vue", None)
JS_PATH = pkg_resources.resource_filename("vuecli", "js")
COMPONENTS_PATH = pkg_resources.resource_filename(
    "anyblok_furetui", "furetui/components")
COMPONENTS_PATH = pkg_resources.resource_filename(
    "anyblok_furetui", "furetui/components")


class FuretUIBlok(Blok):
    """Setup FuretUI for AnyBlok"""
    version = version
    author = 'Suzanne Jean-Sébastien'
    logo = 'static/images/logo.png'

    required = [
        'anyblok-core',
    ]

    css = [
        'static/css/bulma.css',
        'static/css/buefy.min.css',
        'static/css/materialdesignicons.min.css',
    ]
    js = [
        'static/js/buefy.min.js',
        'static/js/vue-router.js',
        'static/js/axios.min.js',
    ]

    templates = [
        'templates/app.tmpl',
        'templates/homepage.tmpl',

        'templates/about.tmpl',
        'templates/login.tmpl',
        'templates/logout.tmpl',
    ]

    components = [
        'components/app.py',
        'components/homepage.py',
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
        config.include('pyramid_jinja2')
        config.add_static_view('/loading.gif', LOADING_CONTENT)
        config.add_static_view('/furet-ui/js', JS_PATH)
        config.add_static_view('/vue', VUE_PATH)
        config.add_static_view('/furetui/components', COMPONENTS_PATH)
        config.add_static_view('/routes', COMPONENTS_PATH)

        config.scan(cls.__module__ + '.views')
