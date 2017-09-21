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
from .pyramid import json_data_adapter, add_mako_and_static
from logging import getLogger
logger = getLogger(__name__)


class FuretUIBlok(Blok):
    version = version
    author = 'Suzanne Jean-Sébastien'
    logo = '../logo.png'

    required = [
        'anyblok-core',
        'anyblok-io-xml',
    ]

    # if connected
    css = [
    ]
    js = [
        '#BLOK/static/furetui.js',
    ]

    # if not connected
    global_css = [
    ]
    global_js = [
        '#BLOK/static/furetui.js',
        '#BLOK/static/login.js',
    ]

    views = [
    ]

    def load(self):
        from os.path import join
        tmpl = Template()
        Blok = self.registry.System.Blok
        for blok in Blok.list_by_state('installed'):
            b = BlokManager.get(blok)
            if hasattr(b, 'views'):
                bpath = BlokManager.getPath(blok)
                for template in b.views:
                    with open(join(bpath, template), 'r') as fp:
                        tmpl.load_file(fp)

        tmpl.compile()
        self.registry.furetui_views = tmpl
        # TODO check all view template exist
        # TODO check if view template are not wrong

    def update(self, latest_version):
        super(FuretUIBlok, self).update(latest_version)
        self.import_file('xml', 'Model.Web.Space.Category',
                         'data', 'spaces.category.xml')

    @classmethod
    def import_declaration_module(cls):
        from . import core  # noqa
        from . import web  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import core
        reload(core)
        from . import web
        reload(web)

    @classmethod
    def pyramid_load_config(cls, config):
        json_data_adapter(config)
        add_mako_and_static(config)
        config.add_route('furetui_main', '/')
        config.add_route('furetui_required_data',
                         '/furetui/init/required/data')
        # config.add_route('furetui_optionnal_data',
        #                  '/furetui/init/optionnal/data')
        # config.add_route('furetui_homepage', '/furetui/homepage')
        config.add_route('furetui_button', '/furetui/button/{buttonId}')
        config.add_route('furetui_custom_view_login',
                         '/furetui/custom/view/Login')
        config.add_route('furetui_custom_view_logout',
                         '/furetui/custom/view/Logout')
        config.add_route('furetui_view', '/furetui/view/{viewId}')
        config.add_route('furetui_space', '/furetui/space/{spaceId}')
        config.add_route('furetui_action', '/furetui/action/{actionId}')
        # config.add_route('furetui_x2x_search', '/furetui/field/x2x/search')
        config.add_route('furetui_x2m_get', '/furetui/list/x2m/get')
        config.add_route('furetui_x2m_view', '/furetui/field/x2m/get/views')
        # config.add_route('furetui_crud_create', '/furetui/data/create')
        config.add_route('furetui_crud_reads', '/furetui/data/read')
        config.add_route('furetui_crud_read', '/furetui/data/read/{dataId}')
        # config.add_route('furetui_crud_update', '/furetui/data/update')
        # config.add_route('furetui_crud_delete', '/furetui/data/delete')
        config.add_route('furetui_crud_search', '/furetui/data/search')
        config.add_route('furetui_login', '/furetui/client/login')
        config.add_route('furetui_logout', '/furetui/client/logout')
        config.scan(cls.__module__ + '.views')
