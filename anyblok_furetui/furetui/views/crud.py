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
from sqlalchemy import or_
from logging import getLogger

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

    def _rec_filter(self, query, Model, keys, searchText):
        field = getattr(Model, keys[0])
        if len(keys) == 1:
            if isinstance(searchText, list):
                query = query.filter(or_(*[field.ilike('%' + st + '%')
                                           for st in searchText]))
            else:
                query = query.filter(field.ilike('%' + searchText + '%'))
        else:
            query = query.join(field)
            query = self._rec_filter(
                query, field.property.mapper.class_, keys[1:], searchText)

        return query

    def getPksFromFilter(self, model, filters):
        pks = []
        try:
            Model = self.registry.get(model)
            query = Model.query()
            if filters:
                for f in filters:
                    query = self._rec_filter(
                        query, Model, f['key'].split('.'), f['value']
                    )

            pks = [x.to_primary_keys() for x in query.all()]
        except AttributeError as e:
            logger.exception(e)

        return pks

    def getDataFor(self, data, Model, pks_list, fields):  # noqa
        model = Model.__registry_name__
        if model not in data:
            data[model] = {}

        fd = Model.fields_description()

        for pks in pks_list:
            if str(pks) not in data[model]:
                data[model][str(pks)] = {}

            entry = Model.from_primary_keys(**pks)
            for field in fields:
                if isinstance(field, list):
                    field, subfield = field
                    _Model = getattr(Model, field).property.mapper.class_
                    if fd[field]['type'] in ('Many2One', 'One2One'):
                        _pks = getattr(entry, field).to_primary_keys()
                        data[model][str(pks)][field] = str(_pks)
                        self.getDataFor(data, _Model, [_pks], subfield)
                    else:
                        _pks = [x.to_primary_keys()
                                for x in getattr(entry, field)]
                        data[model][str(pks)][field] = [str(x) for x in _pks]
                        self.getDataFor(data, _Model, _pks, subfield)

                else:
                    value = getattr(entry, field)
                    if fd[field]['type'] in ('Many2One', 'One2One'):
                        value = str(value.to_primary_keys())
                    elif fd[field]['type'] in ('Many2Many', 'One2Many'):
                        value = [str(x.to_primary_keys()) for x in value]

                    data[model][str(pks)][field] = value

    @view_config(route_name="furetui_crud_reads")
    def furetui_crud_reads(self):
        params = self.request.json_body
        pks = self.getPksFromFilter(params['model'], params['filter'])
        fields = params.get('fields')
        if fields is None or not pks:
            return []

        Model = self.registry.get(params['model'])
        data = {}
        self.getDataFor(data, Model, pks, fields)
        res = [{'type': 'UPDATE_DATA', 'model': m, 'data': d}
               for m, d in data.items()]
        res.append({
            'type': 'UPDATE_VIEW',
            'viewId': params['viewId'],
            'dataIds': [str(x) for x in pks],
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
                    query = Model.query().filter(
                        getattr(Model, fieldname).ilike('%' + params['value'] + '%'))
                    if query.count():
                        search['label'] += ' : ' + params['value']
                        search['value'] = params['value']
                        res.append(search)
                except Exception as e:
                    logger.exception(e)

            elif search.get('type') == 'filter':
                res.append(search)

        return res
