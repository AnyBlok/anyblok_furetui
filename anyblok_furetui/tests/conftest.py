# This file is a part of the AnyBlok project
#
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#    Copyright (C) 2020 Pierre Verkest <pierreverkest84@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok.tests.conftest import *  # noqa F403
from anyblok.tests.conftest import (  # noqa F401
    base_loaded, bloks_loaded, init_registry_with_bloks
)
from anyblok_pyramid.tests.conftest import *  # noqa F403
from pyramid.request import Request


class DummyRequest(Request):
    authenticated_userid = None

    def __init__(self, login, *args, **kwargs):
        self.authenticated_userid = login
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="module")
def add_model_in_registry():
    def add_in_registry(*args, **kwargs):
        """to overwride in modules"""

    return add_in_registry


@pytest.fixture(scope="module")
def shared_data():
    def data(registry):
        """to overwride in modules"""

    return data


@pytest.fixture(scope="module")
def bloks_to_install():
    return []


@pytest.fixture(scope="module")
def init_registry(
    setup_registry, shared_data, add_model_in_registry, bloks_to_install
):
    registry = setup_registry(
        bloks_to_install,
        add_model_in_registry,
    )
    shared_data(registry)
    return registry


@pytest.fixture(scope="function")
def registry(request, init_registry):
    transaction = init_registry.begin_nested()
    request.addfinalizer(init_registry.System.Cache.invalidate_all)
    request.addfinalizer(transaction.rollback)
    return init_registry


@pytest.fixture(scope="module")
def setup_registry(request, bloks_loaded):  # noqa F811
    def setup(bloks, function, **kwargs):
        registry = init_registry_with_bloks(bloks, function, **kwargs)
        request.addfinalizer(registry.close)
        return registry

    return setup
