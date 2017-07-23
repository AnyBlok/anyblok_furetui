# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import os
from pyramid.renderers import JSON
from datetime import datetime
import pytz
import time


def datetime_adapter(obj, request):
    if obj is not None:
        if obj.tzinfo is None:
            timezone = pytz.timezone(time.tzname[0])
            obj = timezone.localize(obj)

    return obj.isoformat()


def json_data_adapter(config):
    json_renderer = JSON()
    json_renderer.add_adapter(datetime, datetime_adapter)
    config.add_renderer('json', json_renderer)
    config.add_renderer('pyramid_rpc:jsonrpc', json_renderer)


def add_mako_and_static(config):
    config.include('pyramid_mako')
    here = os.path.dirname(__file__)
    config.add_static_view('static', os.path.join(here, 'static'))
