# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.column import Integer, String, Boolean, Selection
from anyblok.relationship import Many2One


@Declarations.register(Declarations.Model.FuretUI)
class Menu:
    pass


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Root:
    id = Integer(primary_key=True)
    label = String()
    type = Selection(
        selections={'space': 'Space', 'resource': 'Resource'},
        default='space', nullable=False)
    order = Integer(nullable=False, default=100)
    resource = Many2One(model=Declarations.Model.FuretUI.Resource)
    space = Many2One(model=Declarations.Model.FuretUI.Space)
    # TODO criteria of filter
    # TODO check resource space requirement


@Declarations.register(Declarations.Model.FuretUI.Menu)
class Resource:
    id = Integer(primary_key=True)
    root = Many2One(model=Declarations.Model.FuretUI.Menu.Root,
                    nullable=False)
    label = String(nullable=False)
    order = Integer(nullable=False, default=100)
    resource = Many2One(model=Declarations.Model.FuretUI.Resource,
                        nullable=False)
    default = Boolean(default=False)
    # TODO criteria of filter

# Criteria is hierachical criteria = resource criteria + menu criteria + menu
# root criteria
