from urllib.parse import urlencode

import pytest
from anyblok import Declarations
from anyblok.column import Integer, String
from anyblok.relationship import Many2One
from anyblok.tests.conftest import (base_loaded, bloks_loaded,  # noqa F401
                                    init_registry_with_bloks)
from anyblok_pyramid.bloks.pyramid.restrict import restrict_query_by_user
from pyramid.httpexceptions import HTTPForbidden
# from pyramid.testing import DummyRequest
from pyramid.request import Request

register = Declarations.register
Model = Declarations.Model
Mixin = Declarations.Mixin


class DummyRequest(Request):
    authenticated_userid = None

    def __init__(self, login, *args, **kwargs):
        self.authenticated_userid = login
        super().__init__(*args, **kwargs)


@pytest.fixture(scope="module")
def setup_registry(request, bloks_loaded):  # noqa F811
    def setup(bloks, function, **kwargs):
        registry = init_registry_with_bloks(bloks, function, **kwargs)
        request.addfinalizer(registry.close)
        return registry

    return setup


def add_model_in_registry(*args, **kwargs):
    @register(Model)
    class Team:
        id = Integer(primary_key=True)
        name = String()

    @register(Model.Pyramid)
    class User:
        team = Many2One(model=Model.Team)

    @register(Mixin)
    class TeamOwner:
        team = Many2One(model=Model.Team)

        @restrict_query_by_user()
        def restric_by_user_team(cls, query, user):
            Team = cls.registry.Team
            User = cls.registry.Pyramid.User
            return query.join(Team).join(User).filter(User.login == user.login)

    @register(Model)
    class Order(TeamOwner):
        id = Integer(primary_key=True)
        name = String()


def shared_data(registry):
    team1 = registry.Team.insert(name="Team 1")
    team2 = registry.Team.insert(name="Team 2")
    registry.Pyramid.User.insert(login="user1", team=team1)
    registry.Pyramid.User.insert(login="user2", team=team2)
    registry.Order.insert(name="Order 1.1", team=team1)
    registry.Order.insert(name="Order 2.1", team=team2)
    registry.Order.insert(name="Order 2.2", team=team2)


@pytest.fixture(scope="module")
def init_registry(setup_registry):
    registry = setup_registry(
        ["auth", "furetui"],
        add_model_in_registry,
    )
    shared_data(registry)
    return registry


@pytest.fixture(scope="function")
def registry(request, init_registry):
    transaction = init_registry.begin_nested()
    request.addfinalizer(transaction.rollback)
    return init_registry


def test_create_restrict(registry):
    team1 = registry.Team.query().filter_by(name="Team 1").one()
    with pytest.raises(HTTPForbidden) as ex:
        data = {"name": "test create", "team_id": team1.id}
        registry.FuretUI.CRUD.create(
            "Model.Order",
            "fake_uuid",
            {
                "Model.Order": {"new": {"fake_uuid": data}},
            },
            "user2",
        )
    assert (
        ex.value.detail == f"Your are not allowed to create this object "
        f"Model.Order({{'id': 4}}) with given data: "
        f"{{'name': 'test create', 'team_id': {team1.id}}}"
    )


def test_restrict_read_by_user(registry):
    resutls = registry.FuretUI.CRUD.read(
        DummyRequest(
            "user1",
            {
                "QUERY_STRING": urlencode(
                    query={
                        "context[model]": "Model.Order",
                        "context[fields]": "name",
                    }
                )
            },
        )
    )
    assert resutls["total"] == 1
    assert resutls["data"][0]["data"]["name"] == "Order 1.1"


def test_restrict_read_by_user2(registry):
    resutls = registry.FuretUI.CRUD.read(
        DummyRequest(
            "user2",
            {
                "QUERY_STRING": urlencode(
                    query={
                        "context[model]": "Model.Order",
                        "context[fields]": "name",
                    }
                )
            },
        )
    )
    assert resutls["total"] == 2
    assert [d["data"]["name"] for d in resutls["data"]] == [
        "Order 2.1",
        "Order 2.2",
    ]


def test_update_not_allowed_object(registry):
    order = registry.Order.query().filter_by(name="Order 2.1").one()
    team1 = registry.Team.query().filter_by(name="Team 1").one()
    with pytest.raises(HTTPForbidden) as ex:
        registry.FuretUI.CRUD.update(
            "Model.Order",
            {"id": order.id},
            {
                "Model.Order": {f'[["id",{order.id}]]': {"team_id": team1.id}},
            },
            "user1",
        )
    assert (
        ex.value.detail == f"Your are not allowed to update this object "
        f"Model.Order: {{'id': {order.id}}}."
    )


def test_update_not_allowed_data(registry):
    order = registry.Order.query().filter_by(name="Order 1.1").one()
    team2 = registry.Team.query().filter_by(name="Team 2").one()
    with pytest.raises(HTTPForbidden) as ex:
        data = {"team_id": team2.id}
        registry.FuretUI.CRUD.update(
            "Model.Order",
            {"id": order.id},
            {
                "Model.Order": {f'[["id",{order.id}]]': data},
            },
            "user1",
        )
    assert (
        ex.value.detail == f"Your are not allowed to update this object "
        f"Model.Order({{'id': {order.id}}}) with given data: {data}"
    )


def test_delete_for_user1(registry):
    order = registry.Order.query().filter_by(name="Order 1.1").one()
    registry.FuretUI.CRUD.delete(
        "Model.Order",
        {"id": order.id},
        "user1",
    )


def test_restrict_delete_for_user1(registry):
    order = registry.Order.query().filter_by(name="Order 2.1").one()
    with pytest.raises(HTTPForbidden) as ex:
        registry.FuretUI.CRUD.delete(
            "Model.Order",
            {"id": order.id},
            "user1",
        )
    assert (
        ex.value.detail == f"Your are not allowed to remove this object "
        f"Model.Order: {{'id': {order.id}}}"
    )
