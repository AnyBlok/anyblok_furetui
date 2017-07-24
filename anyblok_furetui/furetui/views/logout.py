# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from pyramid.view import view_config


@view_config(
    route_name='furetui_logout',
    request_method="POST",
    renderer="json"
)
def furetui_logout(request):
    request.session['state'] = "disconnected"
    request.session.save()
    return [
        {
            'type': 'UPDATE_ROUTE',
            'name': 'homepage',
        },
        {
            'type': 'RELOAD',
        },
    ]
