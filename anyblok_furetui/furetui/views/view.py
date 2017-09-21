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
class View():
    def __init__(self, request):
        self.request = request
        self.registry = request.anyblok.registry

    @view_config(route_name="furetui_view")
    def furetui_view(self):
        viewId = self.request.matchdict['viewId']
        params = self.request.json_body
        return [self.registry.Web.View.get_view_render(viewId, params)]

    @view_config(route_name="furetui_x2m_view")
    def furetui_x2m_view(self):
        params = self.request.json_body
        res = []
        for viewId in params.pop('viewIds', []):
            _params = params.copy()
            _params['viewId'] = viewId
            res.append(self.registry.Web.View.get_view_render(viewId, _params))

        return res
