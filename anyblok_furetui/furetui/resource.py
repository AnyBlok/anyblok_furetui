# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from copy import deepcopy
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
    title = String()
    model = String(nullable=False,
                   foreign_key=Declarations.Model.System.Model.use('name'))
    template = String()
    # TODO criteria of filter

    def field_for_(cls, field, fields2read, **kwargs):
        res = {
            'name': field['id'],
            'label': field['label'],
            'component': 'furet-ui-field',
            'type': field['type'].lower(),
        }
        if 'sortable' in kwargs:
            field['sortable'] = bool(eval(kwargs['sortable'], {}, {}))
        if 'help' in kwargs:
            field['tooltip'] = kwargs['help']

        fields2read.append(field['id'])
        for k in field:
            if k in ('id', 'label', 'nullable', 'primary_key'):
                continue
            elif k == 'type':
                res['numeric'] = (
                    True if field['type'] in ('Integer', 'Float', 'Decimal')
                    else False
                )

            elif k == 'model':
                if field[k]:
                    res[k] = field[k]
            else:
                res[k] = field[k]

        return res

    def get_definitions(self):
        Model = self.registry.get(self.model)
        fd = Model.fields_description()
        headers = []
        fields2read = []
        if self.template:
            template = self.registry.furetui_views.get_template(
                self.template, tostring=False)
            for field in template.findall('.//field'):
                attributes = deepcopy(field.attrib)
                field = fd[attributes.pop('name')]
                _type = attributes.pop('type', field['type'])
                meth = 'field_for_' + _type
                if hasattr(self.__class__, meth):
                    headers.append(getattr(self, meth)(
                        field, fields2read, **attributes))
                else:
                    headers.append(self.field_for_(
                        field, fields2read, **attributes))
        else:
            fields = list(fd.keys())
            fields.sort()
            for field_name in fields:
                field = fd[field_name]
                if field['type'] in ('FakeColumn', 'Many2Many', 'One2Many',
                                     'Function'):
                    continue

                meth = 'field_for_' + field['type']
                if hasattr(self, meth):
                    headers.append(getattr(self, meth)(field, fields2read))
                else:
                    headers.append(self.field_for_(field, fields2read))

        return [{
            'id': self.id,
            'type': self.type.label.lower(),
            'title': self.title,
            'model': self.model,
            # 'filters': [],  # TODO
            # 'sort': [],  # TODO
            # 'buttons': [],  # TODO
            # 'on_selected_buttons': [],  # TODO
            'headers': headers,
            'fields': fields2read,
        }]


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
