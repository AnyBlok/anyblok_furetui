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


class InitialisationMixin:

    def getDisconnectedInitialisation(self):
        """Defined the main display of FuretUI when nobody is connected"""
        return [
            {
                'type': 'UPDATE_RIGHT_MENU',
                'value': {
                    'label': 'Login',
                    'image': {'type': 'font-icon', 'value': 'fa-user'},
                },
                'values': [
                    {
                        'label': 'Login',
                        'image': {'type': 'font-icon', 'value': 'fa-user'},
                        'id': 'login',
                        'values': [
                            {
                                'label': 'Login',
                                'description': 'Log in to use the application',
                                'image': {
                                    'type': 'font-icon',
                                    'value': 'fa-user'},
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


@view_defaults(
    request_method="POST",
    renderer="json"
)
class DisconnectedInitialisation(InitialisationMixin):
    @view_config(route_name="furetui_required_data")
    def required_data(self):
        """Return the required data"""
        return self.getDisconnectedInitialisation()


@view_defaults(
    installed_blok=current_blok(),
    request_method="POST",
    renderer="json"
)
class ConnectedInitialisation(InitialisationMixin):
    def __init__(self, request):
        self.request = request
        self.registry = request.anyblok.registry

    def getLeftMenu(self, res):
        """Return The available ``Model.Space``"""
        params = self.request.json_body
        return self.registry.Web.Space.getSpaces(res, params)

    def getRightMenu(self, res):
        """Return the rigth menu information"""
        res.append({
            'type': 'UPDATE_RIGHT_MENU',
            'value': {
                'label': 'Connected',
                'image': {'type': 'font-icon', 'value': 'fa-user'},
            },
            'values': [
                {
                    'label': 'Login',
                    'image': {'type': 'font-icon', 'value': 'fa-user'},
                    'id': 'login',
                    'values': [
                        {
                            'label': 'Logout',
                            'description': 'Disconnect of the application',
                            'image': {
                                'type': 'font-icon',
                                'value': 'fa-user'},
                            'type': 'client',
                            'id': 'Logout',
                        },
                    ],
                },
            ],
        })

    @view_config(route_name="furetui_required_data")
    def required_data(self):
        """Return the required data

        Check in the session if the user is connected and return left and right
        menus else return the disconnect data
        """
        state = self.request.session.get('state')
        if state == 'connected':
            res = []
            self.getRightMenu(res),
            self.getLeftMenu(res),
            return res

        return self.getDisconnectedInitialisation()
