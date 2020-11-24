# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from collections.abc import Mapping
from copy import deepcopy
from .security import exposed_method  # noqa


def merge(dict1, dict2):
    """Return a new dictionary by merging two dictionaries recursively
    In an immutable way

    list are merged as well
    """
    result = deepcopy(dict1)
    for key, value in dict2.items():
        if isinstance(value, Mapping) and isinstance(
            result.get(key, {}), Mapping
        ):
            result[key] = merge(result.get(key, {}), value)
        elif isinstance(value, list) and isinstance(result.get(key, []), list):
            result[key] = result.get(key, [])
            result[key].extend(dict2[key])
        else:
            result[key] = deepcopy(dict2[key])
    return result
