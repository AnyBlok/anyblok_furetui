# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from pyramid.view import view_defaults, view_config
from anyblok_pyramid import current_blok
from logging import getLogger
from json import loads, dumps
from sqlalchemy.exc import ProgrammingError, InternalError

logger = getLogger(__name__)


@view_defaults(
    installed_blok=current_blok(),
    request_method="POST",
    renderer="json"
)
class ConnectedInitialisation():
    def __init__(self, request):
        self.request = request
        self.registry = request.anyblok.registry

    def getDataFor(self, data, Model, pks_list, fields):  # noqa
        model = Model.__registry_name__
        if model not in data:
            data[model] = {}

        fd = Model.fields_description()

        for pks in pks_list:
            if dumps(pks) not in data[model]:
                data[model][dumps(pks)] = {}

            entry = Model.from_primary_keys(**pks)
            for field in fields:
                if isinstance(field, list):
                    field, subfield = field
                    _Model = getattr(Model, field).property.mapper.class_
                    if fd[field]['type'] in ('Many2One', 'One2One'):
                        if getattr(entry, field):
                            _pks = getattr(entry, field).to_primary_keys()
                            data[model][dumps(pks)][field] = dumps(_pks)
                            self.getDataFor(data, _Model, [_pks], subfield)
                    else:
                        _pks = [x.to_primary_keys()
                                for x in getattr(entry, field)]
                        data[model][dumps(pks)][field] = [dumps(x)
                                                          for x in _pks]
                        self.getDataFor(data, _Model, _pks, subfield)

                else:
                    value = getattr(entry, field)
                    if fd[field]['type'] in ('Many2One', 'One2One'):
                        if value:
                            value = dumps(value.to_primary_keys())
                    elif fd[field]['type'] in ('Many2Many', 'One2Many'):
                        value = [dumps(x.to_primary_keys()) for x in value]

                    data[model][dumps(pks)][field] = value

    @view_config(route_name="furetui_crud_reads")
    def furetui_crud_reads(self):
        params = self.request.json_body
        Model = self.registry.get(params['model'])
        pks = Model.getPksFromFilters(params['filter'])
        fields = params.get('fields')
        if fields is None or not pks:
            return []

        data = {}
        self.getDataFor(data, Model, pks, fields)
        res = [{'type': 'UPDATE_DATA', 'model': m, 'data': d}
               for m, d in data.items()]
        res.append({
            'type': 'UPDATE_VIEW',
            'viewId': params['viewId'],
            'dataIds': [dumps(x) for x in pks],
        })
        return res

    @view_config(route_name="furetui_crud_read")
    def furetui_crud_read(self):
        params = self.request.json_body
        pks = self.request.matchdict['dataId']
        fields = params.get('fields')
        if fields is None:
            return []

        Model = self.registry.get(params['model'])
        data = {}
        self.getDataFor(data, Model, [loads(pks)], fields)
        res = [{'type': 'UPDATE_DATA', 'model': m, 'data': d}
               for m, d in data.items()]
        res.append({
            'type': 'UPDATE_VIEW',
            'viewId': params['viewId'],
            'dataIds': [pks],
        })
        return res

    @view_config(route_name="furetui_crud_search")
    def furetui_crud_search(self):
        params = self.request.json_body
        res = []
        for search in params['search']:
            if search.get('type') == 'search':
                try:
                    Model = self.registry.get(search.get('model', params['model']))
                    fieldname = search.get('fieldname', search['key'])
                    query = Model._getPksFromFilterField(
                        Model.query(), getattr(Model, fieldname),
                        params.get('operator', 'ilike'), params['value']
                    )
                    if query.count():
                        search['label'] += ' : ' + params['value']
                        search['value'] = params['value']
                        res.append(search)
                except (ProgrammingError, InternalError):
                    self.registry.rollback()
                except Exception as e:
                    logger.exception(e)

            elif search.get('type') == 'filter':
                res.append(search)

        return res

    @view_config(route_name="furetui_crud_delete")
    def furetui_crud_delete(self):
        params = self.request.json_body
        Model = self.registry.get(params['model'])
        for pks in params['dataIds']:
            Model.query().filter_by(**loads(pks)).delete(
                synchronize_session='fetch')

        res = [{
            'type': 'DELETE_DATA',
            'model': params['model'],
            'dataIds': params['dataIds'],
        }]

        if params.get('path'):
            path = ['', 'space', str(params['path']['spaceId'])]
            if params['path'].get('menuId'):
                path.extend(['menu', str(params['path']['menuId'])])
            path.extend(['action', str(params['path']['actionId'])])
            path.extend(['view', str(params['path']['viewId'])])
            res.append({
                'type': 'UPDATE_ROUTE',
                'path': '/'.join(path),
            })

        return res

    @view_config(route_name="furetui_x2m_get")
    def furetui_x2m_get(self):
        params = self.request.json_body
        fields = params.get('fields')
        if fields is None:
            return []

        Model = self.registry.get(params['model'])
        data = {}
        self.getDataFor(data, Model, [loads(x) for x in params['dataIds']], fields)
        return [{'type': 'UPDATE_DATA', 'model': m, 'data': d}
                for m, d in data.items()]
