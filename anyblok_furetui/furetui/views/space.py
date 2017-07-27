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
class Space():
    def __init__(self, request):
        self.request = request
        self.registry = request.anyblok.registry

    @view_config(route_name="furetui_space")
    def furetui_space(self):
        spaceId = self.request.matchdict['spaceId']
        space = self.registry.Web.Space.query().get(int(spaceId))
        res = [{
            'type': 'UPDATE_SPACE',
            'spaceId': spaceId,
            'left_menu': space.getLeftMenus(),
            'right_menu': space.getRightMenus(),
        }]
        menuId = space.default_menu and str(space.default_menu.id) or ''
        actionId = ''
        if space.default_action:
            actionId = str(space.default_action.id)
        elif menuId and space.default_menu.action:
            actionId = str(space.default_menu.action.id)

        existing_path = self.request.json_body
        path = ['', 'space', spaceId]
        if existing_path.get('menuId', menuId):
            path.extend(['menu', existing_path.get('menuId', menuId)])
        if existing_path.get('actionId', actionId):
            path.extend(['action', existing_path.get('actionId', actionId)])
        if existing_path.get('viewId'):
            path.extend(['view', existing_path['viewId']])
        if existing_path.get('dataId'):
            path.extend(['data', existing_path['dataId']])
        if existing_path.get('mode'):
            path.extend(['mode', existing_path['mode']])

        res.append({
            'type': 'UPDATE_ROUTE',
            'path': '/'.join(path),
        })
        return res
