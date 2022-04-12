# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#    Copyright (C) 2019 Hugo QUEZADA <gohu@hq.netlib.re>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from sqlalchemy import text
from anyblok.declarations import Declarations
from anyblok.column import Integer, String, Boolean, Selection, Json, URL
from anyblok.relationship import Many2One, One2Many
from .translate import Translation


@Declarations.register(Declarations.Model.FuretUI)
class Menu:
    id = Integer(primary_key=True)
    parent_id = Integer(foreign_key='Model.FuretUI.Menu=>id')
    order = Integer(nullable=False, default=100)
    icon_code = String()
    icon_type = String()
    menu_type = Selection(
        selections={
            'Model.FuretUI.Menu.Root': 'Root',
            'Model.FuretUI.Menu.Node': 'Node',
            'Model.FuretUI.Menu.Resource': 'Resource',
            'Model.FuretUI.Menu.Url': 'Url',
            'Model.FuretUI.Menu.Call': 'Call',
        },
        nullable=False)

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Menu, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.FuretUI.Menu':
            mapper_args.update({'polymorphic_on': cls.menu_type})
            mapper_args.update({'polymorphic_identity': None})
        else:
            mapper_args.update({'polymorphic_identity': cls.__registry_name__})

        return mapper_args

    def check_acl(self):
        return True

    def to_dict(self, *a, **kw):
        res = super().to_dict(*a, **kw)
        if 'label' in res and res['label']:
            mapping = self.anyblok.IO.Mapping.get_from_entry(self)
            if mapping:
                lang = self.context.get('lang', 'en')
                res['label'] = Translation.get(
                    lang, f'menu:{mapping.key}', res['label'])

        return res

    @classmethod
    def rec_get_children_menus(cls, children, resource=None):
        res = []
        for child in children:
            if child.check_acl():
                children = []
                definition = child.to_dict(
                    'id', 'order', 'label', 'icon_code', 'icon_type')

                if child.menu_type == 'Model.FuretUI.Menu.Node':
                    children = cls.rec_get_children_menus(
                        child.children, resource=resource)
                elif child.menu_type == 'Model.FuretUI.Menu.Resource':
                    definition['resource'] = child.resource.id
                    definition.update(child.to_dict(
                        'tags', 'order_by', 'filters'))
                elif child.menu_type == 'Model.FuretUI.Menu.Url':
                    definition.update(child.to_dict('url'))
                elif child.menu_type == 'Model.FuretUI.Menu.Call':
                    definition['resource'] = resource.id if resource else None

                    definition.update(child.to_dict('model', 'method'))

                res.append({'children': children, **definition})

        return res

    @classmethod
    def get_menus_from(cls, space=None, resource=None):
        menus = []
        Menu = cls.anyblok.FuretUI.Menu
        MRo = cls.anyblok.FuretUI.Menu.Root
        mros = MRo.query()

        if space is not None:
            mros = mros.filter(MRo.space == space)
        elif resource is not None:
            mros = mros.filter(MRo.resource == resource)

        mros = mros.order_by(MRo.order.asc())
        for mro in mros:
            mres = Menu.query().filter(Menu.parent_id == mro.id)
            mres = mres.order_by(Menu.order.asc()).order_by(Menu.id.asc())
            mres = mres.all()
            if not mres:
                continue

            mres = cls.rec_get_children_menus(
                mro.children, resource=resource)

            if not mres:
                continue

            if mro.label:
                menus.append(
                    {'children': mres, **mro.to_dict(
                        'id', 'order', 'label', 'icon_code', 'icon_type')})
            else:
                menus.extend(mres)

        return menus

    def delete(self, *a, **kw):
        menu_id = self.id
        super().delete(*a, **kw)
        if self.__registry_name__ != 'Model.FuretUI.Menu':
            query = f"delete from furetui_menu where id={menu_id};"
            self.execute_sql_statement(text(query))


@Declarations.register(Declarations.Mixin)
class FuretUIMenuChildren:
    children = One2Many(
        model='Model.FuretUI.Menu',
        primaryjoin=(
            "ModelFuretUIMenu.id == ModelFuretUIMenu.parent_id"
            " and ModelFuretUIMenu.menu_type != 'Model.FuretUI.Menu.Root'"
        )
    )


@Declarations.register(Declarations.Mixin)
class FuretUIMenuParent:
    parent = Many2One(
        model='Model.FuretUI.Menu',
        primaryjoin=(
            "ModelFuretUIMenu.id == ModelFuretUIMenu.parent_id"
            " and ModelFuretUIMenu.menu_type.in_(["
            "'Model.FuretUI.Menu.Root', 'Model.FuretUI.Menu.Node'"
            "])"
        )
    )


@Declarations.register(Declarations.Mixin)
class FuretUIMenu:
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Menu.use('id'))
    label = String(nullable=False)

    def get_i18n_to_export(self, external_id):
        return [(f'menu:{external_id}', self.label)]


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Root(
    Declarations.Model.FuretUI.Menu,
    Declarations.Mixin.FuretUIMenuChildren
):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Menu.use('id'))
    label = String()
    type = Selection(
        selections={'space': 'Space', 'resource': 'Resource'},
        default='space', nullable=False)
    resource = Many2One(model=Declarations.Model.FuretUI.Resource)
    space = Many2One(model=Declarations.Model.FuretUI.Space)
    # TODO check resource space requirement

    def get_i18n_to_export(self, external_id):
        if not self.label:
            return []

        return [(f'menu:{external_id}', self.label)]

    def delete(self, *a, **kw):
        print('titi 1')
        query = f"delete from {self.__tablename__} where id={self.id};"
        print(query)
        self.execute_sql_statement(text(query))
        print('titi 2')
        query = f"delete from furetui_menu where id={self.id};"
        print(query)
        self.execute_sql_statement(text(query))
        print('titi 3')


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Node(
    Declarations.Model.FuretUI.Menu,
    Declarations.Mixin.FuretUIMenu,
    Declarations.Mixin.FuretUIMenuChildren,
    Declarations.Mixin.FuretUIMenuParent
):
    pass


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Resource(
    Declarations.Model.FuretUI.Menu,
    Declarations.Mixin.FuretUIMenu,
    Declarations.Mixin.FuretUIMenuParent
):
    resource = Many2One(model=Declarations.Model.FuretUI.Resource,
                        nullable=False)
    default = Boolean(default=False)
    tags = String()
    order_by = String()
    filters = Json(default={})

    def check_acl(self):
        return self.resource.check_acl()


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Url(
    Declarations.Model.FuretUI.Menu,
    Declarations.Mixin.FuretUIMenu,
    Declarations.Mixin.FuretUIMenuParent
):
    url = URL(nullable=False)


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Call(
    Declarations.Model.FuretUI.Menu,
    Declarations.Mixin.FuretUIMenu,
    Declarations.Mixin.FuretUIMenuParent
):
    model = String(
        nullable=False, size=256,
        foreign_key=Declarations.Model.System.Model.use(
            'name').options(ondelete='cascade'))
    method = String(nullable=False, size=256)

    @classmethod
    def before_insert_orm_event(cls, mapper, connection, target):
        target.is_an_exposed_method()

    @classmethod
    def before_update_orm_event(cls, mapper, connection, target):
        target.is_an_exposed_method()

    def is_an_exposed_method(self):
        """When creating or updating a User.Authorization, check that all rules
        objects exists or return an AuthorizationValidationException

        :exception: AuthorizationValidationException
        """
        if self.method not in self.anyblok.exposed_methods.get(self.model, {}):
            raise Exception(
                f"'{self.model}=>{self.method}' is not an exposed method")
