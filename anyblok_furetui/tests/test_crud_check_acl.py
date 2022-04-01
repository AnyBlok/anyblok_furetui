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
from pyramid.httpexceptions import HTTPForbidden

from .conftest import DummyRequest


@pytest.fixture(scope="module")
def bloks_to_install():
    return ["furetui", "furetui-auth"]


@pytest.fixture(scope="module")
def shared_data():
    def data(registry):
        """to overwride in modules"""
        team = registry.Team.insert(name="test")
        registry.Pyramid.User.insert(team=team, login="user-test")
        pet = registry.Pet.insert(name="Pet test")
        customer = registry.Customer.insert(
            name="Customer test", team=team, pet=pet
        )
        tag1 = registry.Tag.insert(name="Tag test 1", team=team)
        tag2 = registry.Tag.insert(name="Tag test 2", team=team)
        order = registry.Order.insert(name="test", team=team, customer=customer)
        order.tags.extend([tag1, tag2])

    return data


@pytest.fixture
def record(registry):
    return registry.Pet.query().filter_by(name="Pet test").one()


def set_authz(
    registry,
    model="Model.Pet",
    create=False,
    read=False,
    update=False,
    delete=False,
):
    registry.Pyramid.Authorization.insert(
        model=model,
        login="user-test",
        perm_create=dict(matched=create),
        perm_read=dict(matched=read),
        perm_update=dict(matched=update),
        perm_delete=dict(matched=delete),
    )


def test_check_acl_create_forbidden(registry):
    with pytest.raises(HTTPForbidden) as ex:
        registry.FuretUI.CRUD.create(
            "Model.Pet",
            "fake_uuid",
            {
                "Model.Pet": {
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
        "model 'Model.Pet'.",
        ex.value.detail,
    )


def test_check_acl_create(registry):
    set_authz(registry, create=True)
    assert registry, registry.FuretUI.CRUD.create(
        "Model.Pet",
        "fake_uuid",
        {
            "Model.Pet": {
                "new": {
                    "fake_uuid": {
                        "name": "test",
                    }
                }
            },
        },
        "user-test",
    )


@pytest.mark.parametrize(
    "model,fields,expected_error,perms",
    [
        pytest.param(
            "Model.Customer",
            "name",
            "User 'user-test' has to be granted "
            "'read' permission in order to read on "
            "model 'Model.Customer'.",
            [],
            id="Base model",
        ),
        pytest.param(
            "Model.Customer",
            "name,pet.name",
            "User 'user-test' has to be granted "
            "'read' permission in order to read on "
            "model 'Model.Pet'.",
            [
                {"model": "Model.Customer", "perms": {"read": True}},
            ],
            id="One2One",
        ),
        pytest.param(
            "Model.Customer",
            "name,orders.name",
            "User 'user-test' has to be granted "
            "'read' permission in order to read on "
            "model 'Model.Order'.",
            [
                {"model": "Model.Customer", "perms": {"read": True}},
            ],
            id="One2Many",
        ),
        pytest.param(
            "Model.Customer",
            "name,team.name",
            "User 'user-test' has to be granted "
            "'read' permission in order to read on "
            "model 'Model.Team'.",
            [
                {"model": "Model.Customer", "perms": {"read": True}},
            ],
            id="Many2One",
        ),
        pytest.param(
            "Model.Customer",
            "name,orders.name,orders.tags.name",
            "User 'user-test' has to be granted "
            "'read' permission in order to read on "
            "model 'Model.Tag'.",
            [
                {"model": "Model.Customer", "perms": {"read": True}},
                {"model": "Model.Order", "perms": {"read": True}},
            ],
            id="Many2Many",
        ),
    ],
)
def test_check_acl_read_forbidden(
    registry, model, fields, expected_error, perms
):
    for perm in perms:
        set_authz(registry, model=perm["model"], **perm["perms"])
    with registry.FuretUI.context.set(userid="user-test"):
        with pytest.raises(HTTPForbidden) as ex:
            registry.FuretUI.CRUD.read(
                DummyRequest(
                    "user-test",
                    {
                        "QUERY_STRING": urlencode(
                            query={
                                "context[model]": model,
                                "context[fields]": fields,
                            }
                        )
                    },
                )
            )

    assert expected_error == ex.value.detail


@pytest.mark.parametrize(
    "model,fields,expected_total,perms",
    [
        pytest.param(
            "Model.Customer",
            "name",
            1,
            [
                {"model": "Model.Customer", "perms": {"read": True}},
            ],
            id="Base model",
        ),
        pytest.param(
            "Model.Customer",
            "name,pet.name",
            1,
            [
                {"model": "Model.Customer", "perms": {"read": True}},
                {"model": "Model.Pet", "perms": {"read": True}},
            ],
            id="One2one",
        ),
        pytest.param(
            "Model.Customer",
            "name,orders.name",
            1,
            [
                {"model": "Model.Customer", "perms": {"read": True}},
                {"model": "Model.Order", "perms": {"read": True}},
            ],
            id="One2Many",
        ),
        pytest.param(
            "Model.Customer",
            "name,team.name",
            1,
            [
                {"model": "Model.Customer", "perms": {"read": True}},
                {"model": "Model.Team", "perms": {"read": True}},
            ],
            id="Many2One",
        ),
        pytest.param(
            "Model.Customer",
            "name,orders.name,orders.tags.name",
            1,
            [
                {"model": "Model.Customer", "perms": {"read": True}},
                {"model": "Model.Order", "perms": {"read": True}},
                {"model": "Model.Tag", "perms": {"read": True}},
            ],
            id="Many2Many",
        ),
    ],
)
def test_check_acl_read(registry, model, fields, expected_total, perms):
    for perm in perms:
        set_authz(registry, model=perm["model"], **perm["perms"])
    with registry.FuretUI.context.set(userid="user-test"):
        assert (
            registry.FuretUI.CRUD.read(
                DummyRequest(
                    "user-test",
                    {
                        "QUERY_STRING": urlencode(
                            query={
                                "context[model]": model,
                                "context[fields]": fields,
                            }
                        )
                    },
                )
            )["total"]
            == expected_total
        )


def test_check_acl_update_forbidden(registry, record):
    with pytest.raises(HTTPForbidden) as ex:
        registry.FuretUI.CRUD.update(
            "Model.Pet",
            {"id": record.id},
            {
                "Model.Pet": {f'[["id",{record.id}]]': {"name": "renamed"}},
            },
            "user-test",
        )
    assert (
        f"User 'user-test' has to be granted "
        f"'update' permission in order to update this object: "
        f"'Model.Pet({{'id': {record.id}}})'." == ex.value.detail
    )


def test_check_acl_update(registry, record):
    set_authz(registry, update=True)
    with registry.FuretUI.context.set(userid="user-test"):
        assert registry.FuretUI.CRUD.update(
            "Model.Pet",
            {"id": record.id},
            {
                "Model.Pet": {f'[["id",{record.id}]]': {"name": "renamed"}},
            },
            "user-test",
        )


def test_check_acl_delete_forbidden(registry, record):
    with pytest.raises(HTTPForbidden) as ex:
        registry.FuretUI.CRUD.delete(
            "Model.Pet",
            {"id": record.id},
            "user-test",
        )
    assert (
        f"User 'user-test' has to be granted "
        f"'delete' permission in order to delete this object: "
        f"'Model.Pet({{'id': {record.id}}})'." == ex.value.detail
    )


def test_check_acl_delete(registry, record):
    set_authz(registry, delete=True)
    with registry.FuretUI.context.set(userid="user-test"):
        assert (
            registry.FuretUI.CRUD.delete(
                "Model.Pet",
                {"id": record.id},
                "user-test",
            )
            is None
        )
