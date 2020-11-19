# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Pierre Verkest <pierreverkest84@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import re
from urllib.parse import urlencode

import pytest
from anyblok import Declarations
from anyblok.column import Integer, String
from pyramid.httpexceptions import HTTPForbidden

from .conftest import DummyRequest

register = Declarations.register
Model = Declarations.Model
Mixin = Declarations.Mixin


@pytest.fixture(scope="module")
def bloks_to_install():
    return ["furetui", "furetui-auth"]


@pytest.fixture(scope="module")
def add_model_in_registry():
    def add_in_registry(*args, **kwargs):
        @register(Model)
        class Test:
            id = Integer(primary_key=True)
            name = String()

    return add_in_registry


@pytest.fixture(scope="module")
def shared_data():
    def data(registry):
        """to overwride in modules"""
        registry.Pyramid.User.insert(login="user-test")
        registry.Test.insert(name="test")

    return data


@pytest.fixture
def record(registry):
    return registry.Test.query().filter_by(name="test").one()


def set_authz(registry, create=False, read=False, update=False, delete=False):
    registry.Pyramid.Authorization.insert(
        model="Model.Test",
        login="user-test",
        perm_create=dict(matched=create),
        perm_read=dict(matched=read),
        perm_update=dict(matched=update),
        perm_delete=dict(matched=delete),
    )


def test_check_acl_create_forbidden(registry):
    with pytest.raises(HTTPForbidden) as ex:
        registry.FuretUI.CRUD.create(
            "Model.Test",
            "fake_uuid",
            {
                "Model.Test": {
                    "new": {
                        "fake_uuid": {
                            "name": "test",
                        }
                    }
                },
            },
            "user-test",
        )
    assert re.match(
        "User 'user-test' has to be granted "
        "'create' permission in order to create object on "
        "model 'Model.Test'.",
        ex.value.detail,
    )


def test_check_acl_create(registry):
    set_authz(registry, create=True)
    assert registry, registry.FuretUI.CRUD.create(
        "Model.Test",
        "fake_uuid",
        {
            "Model.Test": {
                "new": {
                    "fake_uuid": {
                        "name": "test",
                    }
                }
            },
        },
        "user-test",
    )


def test_check_acl_read_forbidden(registry):
    with pytest.raises(HTTPForbidden) as ex:
        registry.FuretUI.CRUD.read(
            DummyRequest(
                "user-test",
                {
                    "QUERY_STRING": urlencode(
                        query={
                            "context[model]": "Model.Test",
                            "context[fields]": "name",
                        }
                    )
                },
            )
        )
    assert re.match(
        "User 'user-test' has to be granted "
        "'read' permission in order to read on "
        "model 'Model.Test'.",
        ex.value.detail,
    )


def test_check_acl_read(registry):
    set_authz(registry, read=True)
    assert (
        registry.FuretUI.CRUD.read(
            DummyRequest(
                "user-test",
                {
                    "QUERY_STRING": urlencode(
                        query={
                            "context[model]": "Model.Test",
                            "context[fields]": "name",
                        }
                    )
                },
            )
        )["total"]
        == 1
    )


def test_check_acl_update_forbidden(registry, record):
    with pytest.raises(HTTPForbidden) as ex:
        registry.FuretUI.CRUD.update(
            "Model.Test",
            {"id": record.id},
            {
                "Model.Test": {f'[["id",{record.id}]]': {"name": "renamed"}},
            },
            "user-test",
        )
    assert (
        f"User 'user-test' has to be granted "
        f"'update' permission in order to update this object: "
        f"'Model.Test({{'id': {record.id}}})'." == ex.value.detail
    )


def test_check_acl_update(registry, record):
    set_authz(registry, update=True)
    assert registry.FuretUI.CRUD.update(
        "Model.Test",
        {"id": record.id},
        {
            "Model.Test": {f'[["id",{record.id}]]': {"name": "renamed"}},
        },
        "user-test",
    )


def test_check_acl_delete_forbidden(registry, record):
    with pytest.raises(HTTPForbidden) as ex:
        registry.FuretUI.CRUD.delete(
            "Model.Test",
            {"id": record.id},
            "user-test",
        )
    assert (
        f"User 'user-test' has to be granted "
        f"'delete' permission in order to delete this object: "
        f"'Model.Test({{'id': {record.id}}})'." == ex.value.detail
    )


def test_check_acl_delete(registry, record):
    set_authz(registry, delete=True)
    assert (
        registry.FuretUI.CRUD.delete(
            "Model.Test",
            {"id": record.id},
            "user-test",
        )
        is None
    )
