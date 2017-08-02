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


class TestViewMain(PyramidBlokTestCase):

    def connection_state(self, config):
        config.add_route('test_connection_state', '/test/connection/{state}')
        config.add_view(
            update_session_connection, route_name='test_connection_state')

    def setUp(self):
        super(TestViewMain, self).setUp()
        self.includemes.append(self.connection_state)

    def test_get_template_disconnected(self):
        webserver = self.webserver
        resp = webserver.get('/test/connection/disconnected')
        resp = webserver.get('/')
        self.assertEqual(resp.status, '200 OK')

    def test_get_template_connected(self):
        webserver = self.webserver
        webserver.get('/test/connection/connected')
        resp = webserver.get('/')
        self.assertEqual(resp.status, '200 OK')
