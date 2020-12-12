# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from enum import Enum
from cornice.renderer import CorniceRenderer
from anyblok_pyramid.adapter import (
    datetime_adapter, timedelta_adapter_factory, date_adapter,
    uuid_adapter, bytes_adapter, decimal_adapter, enum_adapter)
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


def add_adapters(obj):
    obj.add_adapter(datetime, datetime_adapter)
    obj.add_adapter(Enum, enum_adapter)
    obj.add_adapter(timedelta, timedelta_adapter_factory())
    obj.add_adapter(date, date_adapter)
    obj.add_adapter(UUID, uuid_adapter)
    obj.add_adapter(bytes, bytes_adapter)
    obj.add_adapter(Decimal, decimal_adapter)
    obj.add_adapter(python_pycountry_type, country_adapter)


class FuretUIRender(CorniceRenderer):

    def __init__(self, *args, **kwargs):
        super(FuretUIRender, self).__init__(*args, **kwargs)
        add_adapters(self)


def json_data_adapter(config):
    json_renderer = JSON()
    add_adapters(json_renderer)

    config.add_renderer('json', json_renderer)
    config.add_renderer('cornicejson', FuretUIRender())
    config.add_renderer('pyramid_rpc:jsonrpc', json_renderer)
