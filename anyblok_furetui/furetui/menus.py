# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.column import Integer, String, Boolean, Selection, Json
from anyblok.relationship import Many2One


@Declarations.register(Declarations.Model.FuretUI)
class Menu:
    id = Integer(primary_key=True)
    order = Integer(nullable=False, default=100)
    icon_code = String()
    icon_type = String()


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Root(Declarations.Model.FuretUI.Menu,
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
class Resource(Declarations.Model.FuretUI.Menu):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Menu.use('id'))
    root = Many2One(model=Declarations.Model.FuretUI.Menu.Root,
                    nullable=False, one2many="resources")
    label = String(nullable=False)
    resource = Many2One(model=Declarations.Model.FuretUI.Resource,
                        nullable=False)
    default = Boolean(default=False)
    tags = String()
    order_by = String()
    filters = Json(default={})

    def check_acl(self, authenticated_userid):
        return self.resource.check_acl(authenticated_userid)
