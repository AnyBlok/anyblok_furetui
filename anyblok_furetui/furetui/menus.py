# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.column import Integer, String, Boolean, Selection, Json, URL
from anyblok.relationship import Many2One, One2Many


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

    def check_acl(self, authenticated_userid):
        return True


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

    def check_acl(self, authenticated_userid):
        return self.resource.check_acl(authenticated_userid)


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
