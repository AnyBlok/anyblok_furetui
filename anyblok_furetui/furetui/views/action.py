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


@view_defaults(
    installed_blok=current_blok(),
    request_method="POST",
    renderer="json"
)
class Action():
    def __init__(self, request):
        self.request = request
        self.registry = request.anyblok.registry

    @view_config(route_name="furetui_action")
    def furetui_action(self):
        params = self.request.json_body
        action = self.registry.Web.Action.query().get(int(params['actionId']))
        render = action.render()
        res = [render]
        if not params.get('viewId'):
            params['viewId'] = render['views'][0]['viewId']

        if params.get('menuId'):
            if params.get('dataId'):
                name = 'space_menu_action_view_dataId'
            else:
                name = 'space_menu_action_view'
        else:
            if params.get('dataId'):
                name = 'space_action_view_dataId'
            else:
                name = 'space_action_view'

        res.append({
            'type': 'UPDATE_ROUTE',
            'name': name,
            'params': params,
        })
        return res
