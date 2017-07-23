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
