# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from .template import Template
from anyblok.blok import BlokManager
from os.path import join
from logging import getLogger
from datetime import datetime


logger = getLogger(__name__)


def update_translation(i18n, translations, path=""):
    for key, value in translations.items():
        if not isinstance(key, str):
            raise Exception(
                "The key %r of the path %r must be a string" % key, path)
        elif isinstance(value, dict):
            node = i18n.setdefault(key, {})
            path += key + '.'
            update_translation(node, value)
        elif not isinstance(value, str):
            path += key
            raise Exception(
                "The value %r of the path %r must be a string" % value, path)
        else:
            i18n[key] = value


@Declarations.register(Declarations.Model)
class FuretUI:

    @classmethod
    def pre_load(cls):
        logger.info('Preload furet UI component')
        tmpl_views = Template()
        tmpl_components = Template()
        js = []
        css = []
        i18n = {}
        Blok = cls.registry.System.Blok
        timestamp = datetime.utcnow().timestamp()
        for blok in Blok.list_by_state('installed'):
            b = BlokManager.get(blok)
            bpath = BlokManager.getPath(blok)
            if hasattr(b, 'furetui'):
                for template in b.furetui.get('templates', []):
                    with open(join(bpath, template), 'r') as fp:
                        tmpl_components.load_file(fp)

                js.extend(['%s?%s' % (join('furet-ui', blok, 'js', filename),
                                      timestamp)
                           for filename in b.furetui.get('js', [])])
                css.extend([join('furet-ui', blok, 'css', filename)
                           for filename in b.furetui.get('css', [])])

                for local, translations in b.furetui.get('i18n', {}).items():
                    node = i18n.setdefault(local, {})
                    update_translation(node, translations)

        tmpl_views.compile()
        cls.registry.furetui_views = tmpl_views
        tmpl_components.compile()
        cls.registry.furetui_components = tmpl_components
        cls.registry.furetui_js = js
        cls.registry.furetui_css = css
        cls.registry.furetui_i18n = i18n

    @classmethod
    def get_default_space(cls, authenticated_userid):
        # TODO add default space
        return None

    @classmethod
    def get_i18n(cls):
        return [
            {'locale': key, 'translations': value}
            for key, value in cls.registry.furetui_i18n.items()
        ]

    @classmethod
    def get_templates(cls):
        components = cls.registry.furetui_components
        return {
            known: components.get_template(known, first_children=True)
            for known in components.known
        }

    @classmethod
    def get_js_files(cls):
        return cls.registry.furetui_js

    @classmethod
    def get_css_files(cls):
        return cls.registry.furetui_css

    @classmethod
    def get_global(cls, authenticated_userid):
        # TODO add global variable
        return {'selection_labels': {}}

    @classmethod
    def get_user_menu(cls, authenticated_userid):
        return cls.registry.FuretUI.Menu.User.get_for(authenticated_userid)

    @classmethod
    def get_spaces_menu(cls, authenticated_userid, default_space):
        return cls.registry.FuretUI.Menu.Space.get_for(authenticated_userid)

    @classmethod
    def get_space_menus(cls, authenticated_userid, default_space):
        if not default_space:
            return []

        return cls.registry.FuretUI.Menu.SpaceMenu.get_for(
            authenticated_userid, default_space)
