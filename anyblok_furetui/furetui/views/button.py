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
class Button():
    def __init__(self, request):
        self.request = request
        self.registry = request.anyblok.registry

    @view_config(route_name="furetui_button")
    def furetui_space(self):
        buttonId = self.request.matchdict['buttonId']
        params = self.request.json_body
        Model = self.registry.get(params['model'])
        if 'dataIds' in params:
            dataIds = params.pop('dataIds')
            pks = [eval(x, {}, {}) for x in dataIds]
            params['entries'] = Model.from_multi_primary_keys(*pks)

        return getattr(Model, buttonId)(**params)
