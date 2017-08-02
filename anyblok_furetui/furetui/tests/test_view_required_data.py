# This file is a part of the AnyBlok / FuretUI project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidBlokTestCase
from pyramid.response import Response


def update_session_connection(request):
    state = request.matchdict['state']
    request.session['state'] = state
    request.session.save()
    return Response('ok')


class TestViewRequiredData(PyramidBlokTestCase):

    def connection_state(self, config):
        config.add_route('test_connection_state', '/test/connection/{state}')
        config.add_view(
            update_session_connection, route_name='test_connection_state')

    def setUp(self):
        super(TestViewRequiredData, self).setUp()
        self.includemes.append(self.connection_state)

    def test_disconnected(self):
        webserver = self.webserver
        webserver.get('/test/connection/disconnected')
        resp = webserver.post_json('/furetui/init/required/data', {})
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(
            resp.json,
            [
                {
                    'type': 'UPDATE_RIGHT_MENU',
                    'value': {
                        'label': 'Login',
                        'image': {
                            'type': 'font-icon',
                            'value': 'fa-user',
                        },
                    },
                    'values': [
                        {
                            'label': 'Login',
                            'image': {
                                'type': 'font-icon',
                                'value': 'fa-user',
                            },
                            'id': 'login',
                            'values': [
                                {
                                    'label': 'Login',
                                    'description': (
                                        'Log in to use the application'
                                    ),
                                    'image': {
                                        'type': 'font-icon',
                                        'value': 'fa-user',
                                    },
                                    'type': 'client',
                                    'id': 'Login',
                                },
                            ],
                        },
                    ],
                },
                {
                    'type': 'CLEAR_LEFT_MENU',
                },
            ]
        )

    def testconnected(self):
        webserver = self.webserver
        webserver.get('/test/connection/connected')
        resp = webserver.post_json('/furetui/init/required/data', {})
        self.assertEqual(resp.status, '200 OK')
        self.assertEqual(
            resp.json[0],
            {
                'type': 'UPDATE_RIGHT_MENU',
                'value': {
                    'label': 'Connected',
                    'image': {
                        'type': 'font-icon',
                        'value': 'fa-user',
                    },
                },
                'values': [
                    {
                        'label': 'Login',
                        'image': {
                            'type': 'font-icon',
                            'value': 'fa-user',
                        },
                        'id': 'login',
                        'values': [
                            {
                                'label': 'Logout',
                                'description': 'Disconnect of the application',
                                'image': {
                                    'type': 'font-icon',
                                    'value': 'fa-user',
                                },
                                'type': 'client',
                                'id': 'Logout',
                            },
                        ],
                    },
                ],
            }
        )
