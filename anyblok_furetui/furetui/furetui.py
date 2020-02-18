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
from anyblok.config import Configuration
from os.path import join
from logging import getLogger


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
        views = Template()
        i18n = {}
        Blok = cls.registry.System.Blok
        for blok in Blok.list_by_state('installed'):
            b = BlokManager.get(blok)
            bpath = BlokManager.getPath(blok)
            if hasattr(b, 'furetui'):
                for template in b.furetui.get('views', []):
                    with open(join(bpath, template), 'r') as fp:
                        views.load_file(fp)

                for local, translations in b.furetui.get('i18n', {}).items():
                    node = i18n.setdefault(local, {})
                    update_translation(node, translations)

        views.compile()
        cls.registry.furetui_views = views
        cls.registry.furetui_i18n = i18n

    @classmethod
    def get_default_path(cls, authenticated_userid):
        # TODO add default path on user
        return '/'

    @classmethod
    def get_user_informations(cls, authenticated_userid):
        return [
            {
                'type': 'UPDATE_MENUS',
                'user': [
                    {
                        'name': authenticated_userid,
                        'component': 'furet-ui-appbar-user-dropmenu',
                    },
                ],
            },
            {
                'type': 'LOGIN',
                'userName': authenticated_userid,
            },
        ]

    @classmethod
    def get_logout(cls):
        return [
            {
                'type': 'UPDATE_MENUS',
                'user': [
                    {
                        'name': 'login',
                        'component': 'furet-ui-appbar-head-router-link-button',
                        'props': {'to': '/login', 'label': 'components.login.appbar'},
                    },
                ],
            },
            {'type': 'LOGOUT'},
            {'type': 'UPDATE_ROUTE', 'path': '/'},
        ]

    @classmethod
    def get_initialize(cls, authenticated_userid):
        res = []
        locales = {'en'}
        if not authenticated_userid:
            locale = Configuration.get('furetui_default_locale', 'en')
            locales.add(locale)
        else:
            # TODO
            pass

        res.extend([
            {'type': 'SET_LOCALE', 'locale': locale},
            {'type': 'UPDATE_LOCALES', 'locales': [
                {'locale': l, 'messages': cls.registry.furetui_i18n.get(l, {})}
                for l in locales]}
        ])
        return res
