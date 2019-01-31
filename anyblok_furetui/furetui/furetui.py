# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations


@Declarations.register(Declarations.Model)
class FuretUI:

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
        # TODO add user menus
        return []

    @classmethod
    def get_spaces_menu(cls, authenticated_userid, default_space):
        # TODO add spaces menu
        return []

    @classmethod
    def get_space_menus(cls, authenticated_userid, default_space):
        # TODO add space menus
        return []
