# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from sqlalchemy import text
from anyblok import Declarations
from anyblok.blok import BlokManager
from ..security import exposed_method


@Declarations.register(Declarations.Model.System)
class Blok:

    @exposed_method(is_classmethod=False, permission='admin')
    def furetui_install(self):
        self.anyblok.upgrade(install=(self.name,))
        return [{'type': 'RELOAD'}]

    @exposed_method(is_classmethod=False, permission='admin')
    def furetui_uninstall(self):
        bloks = set()

        def get_inherit_bloks(blok_name):
            bloks.add(blok_name)
            blok = BlokManager.get(blok_name)
            for subblok in (blok.required_by + blok.conditional_by):
                get_inherit_bloks(subblok)

        get_inherit_bloks(self.name)
        print(bloks)
        Blok = self.anyblok.System.Blok
        query = Blok.query().filter(Blok.name.in_(bloks)).order_by(
            Blok.order.desc())

        for blok in query:
            print(blok)
            blok.clean_furetui_datas()

        self.anyblok.upgrade(uninstall=(self.name,))
        return [{'type': 'RELOAD'}]

    @exposed_method(is_classmethod=False, permission='admin')
    def furetui_update(self):
        self.anyblok.upgrade(update=(self.name,))
        return [{'type': 'RELOAD'}]

    def clean_furetui_datas(self):
        Mapping = self.anyblok.IO.Mapping
        # menu
        MENU_TYPES = [
            f'Model.FuretUI.Menu.{x}'
            for x in ['Call', 'Url', 'Resource', 'Node', 'Root']
        ]
        for menu_type in MENU_TYPES:
            query = Mapping.query().filter(
                Mapping.model == menu_type, Mapping.blokname == self.name)
            for mapping in query:
                Mapping.delete(mapping.model, mapping.key, mapping_only=False)

        # space
        query = Mapping.query().filter(
            Mapping.model == 'Model.FuretUI.Space',
            Mapping.blokname == self.name)
        for mapping in query:
            Mapping.delete(mapping.model, mapping.key, mapping_only=False)

        # resource
        RESOURCE_TYPES = [
            f'Model.FuretUI.Resource.{x}'
            for x in ['Set', 'Custom', 'Dashboard', 'Singleton', 'Form',
                      'Filter', 'Tag', 'Thumbnail', 'List']
        ]
        for resource_type in RESOURCE_TYPES:
            query = Mapping.query().filter(
                Mapping.model == resource_type, Mapping.blokname == self.name)
            for mapping in query:
                Mapping.delete(mapping.model, mapping.key, mapping_only=False)

        # access

        for query in ['delete from system_relationship;',
                      'delete from system_column;',
                      'delete from system_field;']:
            self.execute_sql_statement(text(query))
