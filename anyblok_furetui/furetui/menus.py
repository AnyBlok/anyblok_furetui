# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.column import Integer, String, Json, Selection
from anyblok.relationship import Many2One


@Declarations.register(Declarations.Model.FuretUI)
class Menu:
    MENU_TYPE = None

    id = Integer(primary_key=True)
    sequence = Integer(nullable=False, default=100)
    label = String(nullable=False)
    component = String()
    properties = Json(default={})
    login_state = Selection(
        selections={
            'logged': 'Logged',
            'unlogged': 'Unlogged',
            'both': 'Logged and Unlogged',
        }, nullable=False)
    label_is_props = String()
    type = Selection(
        selections={'user': 'User', 'spaces': 'Space',
                    'spaceiMenus': 'Space menus'},
        nullable=False)

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Menu, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.FuretUI.Menu':
            mapper_args.update({'polymorphic_on': cls.type})

        mapper_args.update({'polymorphic_identity': cls.MENU_TYPE})
        return mapper_args

    @classmethod
    def query(cls, *args, **kwargs):
        query = super(Menu, cls).query(*args, **kwargs)
        if cls.__registry_name__ != 'Model.FuretUI.Menu':
            query = query.filter(cls.type == cls.MENU_TYPE)

        return query

    @classmethod
    def update_query_from_authenticated_id(cls, query, authenticated_userid):
        query = query.order_by(cls.sequence)
        if authenticated_userid:
            query = query.filter(cls.login_state.in_(['logged', 'both']))
        else:
            query = query.filter(cls.login_state.in_(['unlogged', 'both']))

        return query

    @classmethod
    def get_for(cls, authenticated_userid):
        # TODO raise if MENU_TYPE is None
        query = cls.query()
        query = cls.update_query_from_authenticated_id(
            query, authenticated_userid)
        return [x.format_menu(authenticated_userid) for x in query]

    def format_menu(self, authenticated_userid):
        menu = {}
        if self.properties:
            menu.update(self.properties)

        menu.update({
            'name': self.id,
            'label': self.label,
        })
        if self.component:
            menu['component'] = self.component

        if self.label_is_props:
            if 'props' not in menu:
                menu['props'] = {}

            menu['props'][self.label_is_props] = self.label

        children = self.registry.FuretUI.Menu.Sub.get_for(
            self, authenticated_userid)
        if children:
            menu['props']['children'] = children

        return menu


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Sub:

    id = Integer(primary_key=True)
    sequence = Integer(nullable=False, default=100)
    label = String(nullable=False)
    properties = Json(default={})
    login_state = Selection(
        selections={
            'logged': 'Logged',
            'unlogged': 'Unlogged',
            'both': 'Logged and Unlogged',
        }, nullable=False, default='both')
    parent = Many2One(model=Declarations.Model.FuretUI.Menu,
                      one2many="children")

    @classmethod
    def update_query_from_authenticated_id(cls, query, authenticated_userid):
        if authenticated_userid:
            query = query.filter(cls.login_state.in_(['logged', 'both']))
        else:
            query = query.filter(cls.login_state.in_(['unlogged', 'both']))

        return query

    @classmethod
    def get_for(cls, parent, authenticated_userid):
        # TODO raise if MENU_TYPE is None
        query = cls.query()
        query = query.filter(cls.parent == parent)
        query = query.order_by(cls.sequence)
        query = cls.update_query_from_authenticated_id(
            query, authenticated_userid)

        query = query.order_by(cls.sequence)
        return [x.format_menu(authenticated_userid) for x in query]

    def format_menu(self, authenticated_userid):
        menu = {}
        if self.properties:
            menu.update(self.properties)

        menu.update({
            'name': self.id,
            'label': self.label,
        })
        return menu


@Declarations.register(Declarations.Model.FuretUI.Menu)
class User(Declarations.Model.FuretUI.Menu):
    MENU_TYPE = 'user'


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Space(Declarations.Model.FuretUI.Menu):
    MENU_TYPE = 'spaces'


@Declarations.register(Declarations.Model.FuretUI.Menu)
class SpaceMenu(Declarations.Model.FuretUI.Menu):
    MENU_TYPE = 'spaceMenus'
    # TODO add dependencies with Space

    @classmethod
    def get_for(cls, authenticated_userid, default_space):
        query = cls.query()
        # TODO check dependencies
        query = cls.update_query_from_authenticated_id(
            query, authenticated_userid)
        return [x.format_menu(authenticated_userid) for x in query]
