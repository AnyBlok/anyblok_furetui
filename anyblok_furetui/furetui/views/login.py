# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration
from pyramid.view import view_config
from sqlalchemy import create_engine


def list_databases():
    """ return the name of the databases found in the BDD

    the result can be filtering by the Configuration entry ``db_filter``

    ..warning::

        For the moment only the ``prostgresql`` dialect is available

    :rtype: list of the database's names
    """
    url = Configuration.get('get_url')()
    db_filter = Configuration.get('db_filter')
    text = None
    if url.drivername in ('postgres', 'postgresql'):
        url = Configuration.get('get_url')(db_name='postgres')
        text = "SELECT datname FROM pg_database"

        if db_filter:
            db_filter = db_filter.replace('%', '%%')
            text += " where datname like '%s'" % db_filter

    if text is None:
        return []

    engine = create_engine(url)
    return [x[0] for x in engine.execute(text).fetchall()
            if x[0] not in ('template1', 'template0', 'postgres')]


@view_config(
    route_name='furetui_custom_view_login',
    request_method="POST",
    renderer="json"
)
def furetui_custom_view_login(request):
    return [{
        'type': 'UPDATE_CLIENT',
        'viewName': 'Login',
        'databases': list_databases(),
        'database': Configuration.get('get_db_name')(request)
    }]


@view_config(
    route_name='furetui_login',
    request_method="POST",
    renderer="json"
)
def furetui_login(request):
    database = request.json_body.get('database')
    request.session['database'] = database
    request.session['state'] = "connected"
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
