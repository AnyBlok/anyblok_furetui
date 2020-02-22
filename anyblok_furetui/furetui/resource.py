# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.column import Integer, String, Boolean, Selection
from anyblok.relationship import Many2One


@Declarations.register(Declarations.Model.FuretUI)
class Resource:

    id = Integer(primary_key=True)
    type = Selection(
        selections={
            'Model.FuretUI.Resource.Custom': 'Custom',
            'Model.FuretUI.Resource.Set': 'Set',
            'Model.FuretUI.Resource.List': 'List',
            'Model.FuretUI.Resource.Thumbnail': 'Thumbnail',
            'Model.FuretUI.Resource.Form': 'Form',
            'Model.FuretUI.Resource.Dashboard': 'Dashboard',
        },
        nullable=False)

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Resource, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.FuretUI.Resource':
            mapper_args.update({'polymorphic_on': cls.type})
            mapper_args.update({'polymorphic_identity': None})
        else:
            mapper_args.update({'polymorphic_identity': cls.__registry_name__})

        return mapper_args

    def get_definitions(self):
        raise Exception('This method must be over right')

    def to_dict(self, *a, **kw):
        res = super(Resource, self).to_dict(*a, **kw)
        if 'type' in res:
            res['type'] = self.type.label.lower()

        return res

    def get_menus(self):
        menus = []
        MRe = self.registry.FuretUI.Menu.Resource
        MRo = self.registry.FuretUI.Menu.Root
        mros = MRo.query().filter(MRo.resource == self)
        mros = mros.order_by(MRo.order.desc())
        for mro in mros:
            mres = MRe.query().filter(MRe.root == mro)
            mres = mres.order_by(MRe.order.desc()).order_by(MRe.id.asc())
            mres = mres.all()
            if not mres:
                continue

            mres = [{'resource': mre.resource.id,
                     **mre.to_dict('id', 'order', 'label')}
                    for mre in mres]
            if mro.label:
                menus.append(
                    {'children': mres, **mro.to_dict('id', 'order', 'label')})
            else:
                menus.extend(mres)

        return menus


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Custom(Declarations.Model.FuretUI.Resource):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use('id'))
    component = String(nullable=False)

    def get_definitions(self):
        return [self.to_dict()]


@Declarations.register(Declarations.Model.FuretUI.Resource)
class List(Declarations.Model.FuretUI.Resource):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use('id'))
    model = String(nullable=False,
                   foreign_key=Declarations.Model.System.Model.use('name'))
    template = String(nullable=False)
    # TODO criteria of filter


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Thumbnail(Declarations.Model.FuretUI.Resource):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use('id'))
    model = String(nullable=False,
                   foreign_key=Declarations.Model.System.Model.use('name'))
    template = String(nullable=False)
    # TODO criteria of filter


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Form(Declarations.Model.FuretUI.Resource):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use('id'))
    model = String(foreign_key=Declarations.Model.System.Model.use('name'))
    template = String()
    is_polymorphic = Boolean(default=False)
    # TODO field Selection RO / RW / WO


@Declarations.register(Declarations.Model.FuretUI.Resource)
class PolymorphicForm():
    parent = Many2One(model=Declarations.Model.FuretUI.Resource.Form,
                      primary_key=True, one2many="child")
    model = String(primary_key=True,
                   foreign_key=Declarations.Model.System.Model.use('name'))
    # Add another field type string and removes model because model
    # is already on resource
    resource = Many2One(model=Declarations.Model.FuretUI.Resource.Form)


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Set(Declarations.Model.FuretUI.Resource):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use('id'))
    form = Many2One(model=Declarations.Model.FuretUI.Resource.Form,
                    nullable=False)
    list = Many2One(model=Declarations.Model.FuretUI.Resource.List)
    thumbnail = Many2One(model=Declarations.Model.FuretUI.Resource.Thumbnail)
    # TODO add checkonstraint on multi + select
    # TODO add form new for create
    # TODO add boolean can_create, can_modify, can_delete
