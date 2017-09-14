# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from sqlalchemy import or_


@Declarations.register(Declarations.Core)
class Base:

    @classmethod
    def _getPksFromFilterField(cls, query, field, operator, value):
        raise Exception('No filter for no SQL Model')

    @classmethod
    def getPksFromFilters(cls, filters):
        raise Exception('No filter for no SQL Model')

    @classmethod
    def get_display_fields(cls, mode=None):
        raise Exception('No fields for no SQL Model')

    @classmethod
    def get_default_action(cls, mode=None):
        raise Exception('No fields for no SQL Model')

    @classmethod
    def get_default_menu_linked_with_action(cls, action=None, mode=None):
        raise Exception('No fields for no SQL Model')

    @classmethod
    def get_default_views_linked_with_action(cls, action=None, mode=None):
        raise Exception('No fields for no SQL Model')


@Declarations.register(Declarations.Core)
class SqlBase:

    @classmethod
    def getRemoteModelFor(cls, fieldname):
        Field = cls.registry.System.Field
        query = Field.query()
        models = [cls.__registry_name__]
        for base in cls.__anyblok_bases__:
            models.append(base.__registry_name__)

        query = query.filter(Field.model.in_(models))
        query = query.filter(Field.name == fieldname)
        field = query.first()
        if field.remote_model:
            return cls.registry.get(field.remote_model)

        return None

    @classmethod
    def _getPksFromFilterField(cls, query, field, operator, value):
        if isinstance(value, list):
            return query.filter(or_(*[field.ilike('%' + st + '%')
                                      for st in value]))

        return query.filter(field.ilike('%' + value + '%'))

    @classmethod
    def _getPksFromFilter(cls, query, keys, operator, value):
        field = getattr(cls, keys[0])
        if len(keys) == 1:
            query = cls._getPksFromFilterField(query, field, operator, value)
        else:
            query = query.join(field)
            Model = cls.getRemoteModelFor(keys[0])
            query = Model._getPksFromFilter(query, keys[1:], operator, value)

        return query

    @classmethod
    def getPksFromFilters(cls, filters):
        query = cls.query()
        for f in filters:
            query = cls._getPksFromFilter(
                query, f['key'].split('.'), f.get('operator', 'ilike'),
                f['value']
            )

        return [x.to_primary_keys() for x in query.all()]

    @classmethod
    def __get_display_fields(cls, mode=None):
        if hasattr(cls, '__x2m_display_fields'):
            if isinstance(cls.__x2m_display_fields, list):
                return cls.__x2m_display_fields

            return [cls.__x2m_display_fields]

        return []

    @classmethod
    def __get_display_fields_from_columns(cls, mode=None):
        Column = cls.registry.System.Column
        query = Column.query()
        models = [cls.__registry_name__]
        for base in cls.__anyblok_bases__:
            models.append(base.__registry_name__)

        query = query.filter(Column.model.in_(models))
        query = query.filter(Column.ftype.in_(['String', 'uString']))
        query = query.order_by(Column.name)
        fields = query.all().name

        for field in ('title', 'name', 'subject', 'label'):
            if field in fields:
                return [field]

        return fields

    @classmethod
    def get_display_fields(cls, mode=None):
        fields = cls.__get_display_fields(mode=mode)
        if not fields:
            fields = cls.__get_display_fields_from_columns(mode=mode)

        return fields

    @classmethod
    def get_default_action(cls, mode=None):
        Action = cls.registry.Web.Action
        query = Action.query().filter(Action.model == cls.__registry_name__)
        query = query.limit(1)
        return query.one_or_none()

    @classmethod
    def get_default_menu_linked_with_action(cls, action=None, mode=None):
        Menu = cls.registry.Web.Menu
        query = Menu.query().filter(Menu.action == action)
        query = query.order_by(Menu.order)
        query = query.limit(1)
        return query.one_or_none()

    @classmethod
    def get_default_views_linked_with_action(cls, action=None, mode=None):
        if action:
            if action.views:
                views = [
                    {
                        'viewId': v.id,
                        'type': v.mode.split('.')[-1],
                        'order': v.order,
                        'unclickable': v.unclickable,
                    }
                    for v in action.views
                ]
            else:
                views = [
                    {
                        'viewId': 'List-%d' % action.id,
                        'order': 1,
                        'type': 'List',
                    },
                    {
                        'viewId': 'Form-%d' % action.id,
                        'order': 2,
                        'type': 'Form',
                        'unclickable': '1',
                    },
                ]
        else:
            views = []

        return sorted(views, key=lambda k: k['order'])
