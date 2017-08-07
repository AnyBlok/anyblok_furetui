# This file is a part of the AnyBlok / FuretUI project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidBlokTestCase
from json import dumps


class TestViewCrudRead(PyramidBlokTestCase):

    def test_reads_without_filter(self):
        resp = self.webserver.post_json('/furetui/data/read', {
            'model': 'Model.System.Model',
            'filter': [],
            'fields': ['name', 'table'],
            'viewId': 'View-1',
        })
        entries = self.registry.System.Model.query().all()
        expected = [
            {
                'type': 'UPDATE_DATA',
                'model': 'Model.System.Model',
                'data': {
                    dumps(x.to_primary_keys()): {
                        'name': x.name,
                        'table': x.table,
                    }
                    for x in entries
                },
            },
            {
                'type': 'UPDATE_VIEW',
                'viewId': 'View-1',
                'dataIds': [
                    dumps(x.to_primary_keys())
                    for x in entries
                ],
            },
        ]
        self.assertEqual(resp.json, expected)

    def test_reads_with_filter(self):
        resp = self.webserver.post_json('/furetui/data/read', {
            'model': 'Model.System.Model',
            'filter': [{'key': 'name', 'value': 'web'}],
            'fields': ['name', 'table'],
            'viewId': 'View-1',
        })
        Model = self.registry.System.Model
        entries = Model.query().filter(Model.name.ilike('%web%')).all()
        expected = [
            {
                'type': 'UPDATE_DATA',
                'model': 'Model.System.Model',
                'data': {
                    dumps(x.to_primary_keys()): {
                        'name': x.name,
                        'table': x.table,
                    }
                    for x in entries
                },
            },
            {
                'type': 'UPDATE_VIEW',
                'viewId': 'View-1',
                'dataIds': [
                    dumps(x.to_primary_keys())
                    for x in entries
                ],
            },
        ]
        self.assertEqual(resp.json, expected)

    def test_read(self):
        Model = self.registry.System.Model
        entry = Model.query().first()
        resp = self.webserver.post_json(
            '/furetui/data/read/%s' % dumps(entry.to_primary_keys()),
            {
                'model': 'Model.System.Model',
                'fields': ['name', 'table'],
                'viewId': 'View-1',
            }
        )
        expected = [
            {
                'type': 'UPDATE_DATA',
                'model': 'Model.System.Model',
                'data': {
                    dumps(entry.to_primary_keys()): {
                        'name': entry.name,
                        'table': entry.table,
                    }
                },
            },
            {
                'type': 'UPDATE_VIEW',
                'viewId': 'View-1',
                'dataIds': [dumps(entry.to_primary_keys())],
            },
        ]
        self.assertEqual(resp.json, expected)
