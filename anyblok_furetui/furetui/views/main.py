# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration
from anyblok.registry import RegistryManager
from anyblok.blok import BlokManager
from pyramid.view import view_config
from pyramid.renderers import render_to_response


def format_static(blok, static_url):
    """ Replace the attribute #BLOK by the real name of the blok

    :param blok: the blok's name
    :param static_url: the url to format
    :rtype: str, formated url
    """
    if static_url.startswith('#BLOK'):
        return '/' + blok + static_url[5:]
    else:
        return static_url


def get_static(static_type):
    """ Get in the Blok definition the static data from the client

    :param static: entry to read: css, js, ...
    :rtype: list of str
    """
    res = []
    for blok_name in BlokManager.ordered_bloks:
        blok = BlokManager.get(blok_name)
        if hasattr(blok, static_type):
            for static_url in getattr(blok, static_type):
                res.append(format_static(blok_name, static_url))

    return res


@view_config(route_name='furetui_main')
def load_main(request):
    """ Return the client main page
    """
    dbname = Configuration.get('get_db_name')(request)
    state = request.session.get('state')

    if state == 'connected':
        registry = RegistryManager.get(dbname)
        css = registry.Web.get_css()
        js = registry.Web.get_js()
    else:
        css = get_static('global_css')
        js = get_static('global_js')

    title = Configuration.get('app_name', 'AnyBlok / FuretUI')
    return render_to_response('anyblok_furetui:client.mak',
                              {'title': title,
                               'css': css,
                               'js': js,
                               }, request=request)
