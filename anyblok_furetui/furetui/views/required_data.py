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

    def getLeftMenu(self):
        values = []
        value = {
            'label': '',
            'image': {'type': 'font-icon', 'value': ''},
        }
        space = None
        Category = self.registry.Web.Space.Category
        Space = self.registry.Web.Space
        for c in Category.query().order_by(Category.order).all():
            query = Space.query().filter(Space.category == c)
            query = query.order_by(Space.order)
            if query.count():
                categ = {
                    'id': str(c.id),
                    'label': c.label,
                    'image': {'type': 'font-icon', 'value': c.icon},
                    'values': [],
                }
                values.append(categ)
                for s in query.all():
                    categ['values'].append({
                        'id': str(s.id),
                        'label': s.label,
                        'description': s.description,
                        'type': s.type,
                        'image': {'type': 'font-icon', 'value': s.icon},
                    })

        if (values):
            value['label'] = values[0]['values'][0]['label']
            value['image'] = values[0]['values'][0]['image']
            space = int(values[0]['values'][0]['id'])

        return space, {
            'type': 'UPDATE_LEFT_MENU',
            'value': value,
            'values': values,
        }

    def getSpacePath(self, space):
        return {}

    def getRightMenu(self):
        return {
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
        }

    @view_config(route_name="furetui_required_data")
    def required_data(self):
        state = self.request.session.get('state')
        if state == 'connected':
            space, left = self.getLeftMenu()
            res = [
                self.getRightMenu(),
                left,
                # self.getSpacePath(space),
            ]
            return res

        return self.getDisconnectedInitialisation()
