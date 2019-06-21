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


@Declarations.register(Declarations.Model)
class FuretUI:

    @classmethod
    def pre_load(cls):
        # TODO add cache classmethod
        tmpl_views = Template()
        tmpl_components = Template()
        js = []
        css = []
        Blok = cls.registry.System.Blok
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
        cls.registry.furetui_views = tmpl_views
        tmpl_components.compile()
        cls.registry.furetui_components = tmpl_components
        cls.registry.furetui_js = js
        cls.registry.furetui_css = css

    @classmethod
    def get_default_space(cls, authenticated_userid):
        # TODO add default space
        return None

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
        return {}

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
