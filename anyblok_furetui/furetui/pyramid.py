# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.adapter import (
    datetime_adapter, timedelta_adapter_factory, date_adapter,
    uuid_adapter, bytes_adapter, decimal_adapter)
from pyramid.renderers import JSON
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal

python_pycountry_type = None
try:
    import pycountry
    if not pycountry.countries._is_loaded:
        pycountry.countries._load()

    python_pycountry_type = pycountry.countries.data_class
except ImportError:
    pass


def country_adapter(country, request):
    if country is None:
        return None

    return country.alpha_3


def json_data_adapter(config):
    json_renderer = JSON()
    json_renderer.add_adapter(datetime, datetime_adapter)
    json_renderer.add_adapter(timedelta, timedelta_adapter_factory())
    json_renderer.add_adapter(date, date_adapter)
    json_renderer.add_adapter(UUID, uuid_adapter)
    json_renderer.add_adapter(bytes, bytes_adapter)
    json_renderer.add_adapter(Decimal, decimal_adapter)
    json_renderer.add_adapter(python_pycountry_type, country_adapter)

    config.add_renderer('json', json_renderer)
    config.add_renderer('pyramid_rpc:jsonrpc', json_renderer)
