# This file is a part of the AnyBlok / FuretUI project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidBlokTestCase


class TestViewAction(PyramidBlokTestCase):

    def test_view(self):
        Action = self.registry.Web.Action
        action = Action.insert(model="Model.System.Model", label="Model")
        webserver = self.webserver
        resp = webserver.post_json('/furetui/action/%d' % action.id, {})
        self.assertEqual(
            resp.json,
            [
                {
                    'type': 'UPDATE_ACTION',
                    'actionId': str(action.id),
                    'label': 'Model',
                    'selected_view': 'List-%d' % action.id,
                    'views': [
                        {
                            'type': 'List',
                            'viewId': 'List-%d' % action.id,
                        },
                        {
                            'type': 'Form',
                            'unclickable': True,
                            'viewId': 'Form-%d' % action.id,
                        }
                    ]
                },
                {
                    'type': 'UPDATE_ROUTE',
                    'name': 'space_action_view',
                    'params': {
                        'viewId': 'List-%d' % action.id,
                    },
                }
            ]
        )

    def test_view_with_menu(self):
        Action = self.registry.Web.Action
        action = Action.insert(model="Model.System.Model", label="Model")
        webserver = self.webserver
        resp = webserver.post_json('/furetui/action/%d' % action.id, {
            'spaceId': 'test1',
            'menuId': 'test2',
        })
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'name': 'space_menu_action_view',
                'params': {
                    'spaceId': 'test1',
                    'menuId': 'test2',
                    'viewId': 'List-%d' % action.id,
                },
            }
        )

    def test_view_with_menu_and_data(self):
        Action = self.registry.Web.Action
        action = Action.insert(model="Model.System.Model", label="Model")
        webserver = self.webserver
        resp = webserver.post_json('/furetui/action/%d' % action.id, {
            'spaceId': 'test1',
            'menuId': 'test2',
            'dataId': 'test3',
            'mode': 'test4',
        })
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'name': 'space_menu_action_view_dataId',
                'params': {
                    'spaceId': 'test1',
                    'menuId': 'test2',
                    'viewId': 'List-%d' % action.id,
                    'dataId': 'test3',
                    'mode': 'test4',
                },
            }
        )

    def test_view_with_data(self):
        Action = self.registry.Web.Action
        action = Action.insert(model="Model.System.Model", label="Model")
        webserver = self.webserver
        resp = webserver.post_json('/furetui/action/%d' % action.id, {
            'spaceId': 'test1',
            'dataId': 'test3',
            'mode': 'test4',
        })
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'name': 'space_action_view_dataId',
                'params': {
                    'spaceId': 'test1',
                    'viewId': 'List-%d' % action.id,
                    'dataId': 'test3',
                    'mode': 'test4',
                },
            }
        )
