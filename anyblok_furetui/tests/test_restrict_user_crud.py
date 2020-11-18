import re
from urllib.parse import urlencode

import pytest
from anyblok import Declarations
from anyblok.column import Integer, String
from anyblok.relationship import Many2Many, Many2One
from anyblok.tests.conftest import (  # noqa F401
    base_loaded,
    bloks_loaded,
    init_registry_with_bloks,
)
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
            User = cls.registry.Pyramid.User
            return (
                query.join(cls.team).join(User).filter(User.login == user.login)
            )

    @register(Model)
    class Customer(Mixin.TeamOwner):
        id = Integer(primary_key=True)
        name = String()

    @register(Model)
    class Tag(Mixin.TeamOwner):
        id = Integer(primary_key=True)
        name = String()

    @register(Model)
    class Order(Mixin.TeamOwner):
        id = Integer(primary_key=True)
        name = String()
        customer = Many2One(model=Model.Customer, one2many="orders")
        tags = Many2Many(
            model=Model.Tag,
            join_table="join_order_tag",
            remote_columns="id",
            local_columns="id",
            m2m_remote_columns="tag_id",
            m2m_local_columns="order_id",
            many2many="orders",
        )


def shared_data(registry):
    team1 = registry.Team.insert(name="Team 1")
    team2 = registry.Team.insert(name="Team 2")
    registry.Pyramid.User.insert(login="user1", team=team1)
    registry.Pyramid.User.insert(login="user2", team=team2)
    tag10 = registry.Tag.insert(name="Tag 1.0", team=team1)
    tag11 = registry.Tag.insert(name="Tag 1.1", team=team1)
    registry.Tag.insert(name="Tag 2.0", team=team2)
    tag2 = registry.Tag.insert(name="Tag 2.1", team=team2)
    tag22 = registry.Tag.insert(name="Tag 2.2", team=team2)
    customer1 = registry.Customer.insert(name="Customer 1", team=team1)
    customer2 = registry.Customer.insert(name="Customer 2", team=team2)
    registry.Order.insert(name="Order 1.1", team=team1, customer=customer1)
    order12 = registry.Order.insert(
        name="Order 1.2", team=team1, customer=customer1
    )
    registry.Order.insert(name="Order 1.3", team=team1, customer=customer1)
    order12.tags.extend([tag10, tag11])
    order21 = registry.Order.insert(
        name="Order 2.1", team=team2, customer=customer2
    )
    order22 = registry.Order.insert(
        name="Order 2.2", team=team2, customer=customer2
    )
    order21.tags.append(tag2)
    order22.tags.extend([tag2, tag22])


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
    assert re.match(
        f"You are not allowed to create this object "
        f"Model.Order\({{'id': \d+}}\) with given data: "  # noqa W605
        f"{{'name': 'test create', 'team_id': {team1.id}}}$",
        ex.value.detail,
    )


def test_restrict_read_by_user(registry):
    results = registry.FuretUI.CRUD.read(
        DummyRequest(
            "user1",
            {
                "QUERY_STRING": urlencode(
                    query={
                        "context[model]": "Model.Order",
                        "context[fields]": "name,customer.name,tags.name",
                    }
                )
            },
        )
    )
    assert results["total"] == 3
    assert [
        d["data"]["name"]
        for d in results["data"]
        if d["model"] == "Model.Order"
    ] == [
        "Order 1.1",
        "Order 1.2",
        "Order 1.3",
    ]


def test_restrict_read_by_user2(registry):
    results = registry.FuretUI.CRUD.read(
        DummyRequest(
            "user2",
            {
                "QUERY_STRING": urlencode(
                    query={
                        "context[model]": "Model.Order",
                        "context[fields]": "name,customer.name,tags.name",
                    }
                )
            },
        )
    )
    assert results["total"] == 2
    assert [
        d["data"]["name"]
        for d in results["data"]
        if d["model"] == "Model.Order"
    ] == [
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
        ex.value.detail == f"You are not allowed to update this object "
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
        ex.value.detail == f"You are not allowed to update this object "
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
        ex.value.detail == f"You are not allowed to remove this object "
        f"Model.Order: {{'id': {order.id}}}"
    )


def create_o2m(
    registry,
    customer_team="Team 1",
    new_order_team="Team 1",
    linked_order="Order 1.1",
    updated_order="Order 1.2",
    updated_order_team="Team 1",
    new_tag_team="Team 1",
    linked_tag="Tag 1.0",
    updated_tag="Tag 1.1",
    updated_tag_team="Team 1",
):
    customer_team_ = registry.Team.query().filter_by(name=customer_team).one()
    new_order_team_ = registry.Team.query().filter_by(name=new_order_team).one()
    linked_order_ = registry.Order.query().filter_by(name=linked_order).one()
    updated_order_ = registry.Order.query().filter_by(name=updated_order).one()
    updated_order_team_ = (
        registry.Team.query().filter_by(name=updated_order_team).one()
    )

    new_tag_team_ = registry.Team.query().filter_by(name=new_tag_team).one()
    linked_tag_ = registry.Tag.query().filter_by(name=linked_tag).one()
    updated_tag_ = registry.Tag.query().filter_by(name=updated_tag).one()
    updated_tag_team_ = (
        registry.Team.query().filter_by(name=updated_tag_team).one()
    )

    return registry.FuretUI.CRUD.create(
        "Model.Customer",
        "fake_uuid",
        {
            "Model.Customer": {
                "new": {
                    "fake_uuid": {
                        "name": "Jean-Sébastien",
                        "team": {"id": customer_team_.id},
                        "orders": [
                            {
                                "__x2m_state": "ADDED",
                                "uuid": "fake_uuid_order_1",
                            },
                            {
                                "__x2m_state": "LINKED",
                                "id": linked_order_.id,
                            },
                            {
                                "__x2m_state": "UPDATED",
                                "id": updated_order_.id,
                            },
                        ],
                    },
                }
            },
            "Model.Order": {
                "new": {
                    "fake_uuid_order_1": {
                        "name": "Order 1.3",
                        "team": {"id": new_order_team_.id},
                        "tags": [
                            {
                                "__x2m_state": "LINKED",
                                "id": linked_tag_.id,
                            },
                            {
                                "__x2m_state": "UPDATED",
                                "id": updated_tag_.id,
                            },
                            {
                                "__x2m_state": "ADDED",
                                "uuid": "fake_uuid_tag_13",
                            },
                        ],
                    }
                },
                f'[["id",{updated_order_.id}]]': {
                    "name": "Order renamed",
                    "team_id": updated_order_team_.id,
                },
            },
            "Model.Tag": {
                "new": {
                    "fake_uuid_tag_13": {
                        "name": "Tag 1.3",
                        "team_id": new_tag_team_.id,
                    }
                },
                f'[["id",{updated_tag_.id}]]': {
                    "name": "Tag renamed",
                    "team_id": updated_tag_team_.id,
                },
            },
        },
        "user1",
    )


def test_create_o2m(registry):
    assert create_o2m(registry)


@pytest.mark.parametrize(
    "config,expected_regex_error_message",
    [
        pytest.param(
            {"updated_tag_team": "Team 2"},
            r"You are not allowed to update this object "
            r"Model.Tag\({'id': \d+}\) with given data",
            id="restricted m2m updating tag with team2",
        ),
        pytest.param(
            {"updated_tag": "Tag 2.1"},
            r"You are not allowed to update this object "
            r"Model.Tag: {'id': \d+}.$",
            id="restricted m2m updating team2's tag",
        ),
        pytest.param(
            {"linked_tag": "Tag 2.1"},
            r"You are not allowed to link this object "
            r"Model.Tag\({'id': \d+}\) with <Model.Order\(",
            id="restricted m2m linking team2's tag",
        ),
        pytest.param(
            {"new_tag_team": "Team 2"},
            r"You are not allowed to create this object "
            r"Model.Tag\({'id': \d+}\) with given data: ",
            id="restricted m2m creating team2's tag",
        ),
        pytest.param(
            {"updated_order_team": "Team 2"},
            r"You are not allowed to update this object "
            r"Model.Order\({'id': \d+}\) with given data",
            id="restricted o2m updating order with team2",
        ),
        pytest.param(
            {"updated_order": "Order 2.1"},
            r"You are not allowed to update this object "
            r"Model.Order: {'id': \d+}.$",
            id="restricted o2m updating team2's order",
        ),
        pytest.param(
            {"linked_order": "Order 2.1"},
            r"You are not allowed to link this object "
            r"Model.Order\({'id': \d+}\) with <Model.Customer\(",
            id="restricted o2m linking team2's order",
        ),
        pytest.param(
            {"new_order_team": "Team 2"},
            r"You are not allowed to create this object "
            r"Model.Order\({'id': \d+}\) with given data: ",
            id="restricted o2m creating team2's order",
        ),
        pytest.param(
            {"customer_team": "Team 2"},
            r"You are not allowed to create this object "
            r"Model.Customer\({'id': \d+}\) with given data: ",
            id="restricted m2o customer team 2",
        ),
    ],
)
def test_restricted_create_o2m(registry, config, expected_regex_error_message):
    with pytest.raises(HTTPForbidden) as ex:
        create_o2m(registry, **config)
    assert re.match(expected_regex_error_message, ex.value.detail)


def update_o2m(
    registry,
    updated_customer="Customer 1",
    deleted_order="Order 1.1",
    updated_order="Order 1.2",
    unlinked_order="Order 1.3",
    deleted_tag="Tag 1.0",
    unlinked_tag="Tag 1.1",
):
    updated_customer_ = (
        registry.Customer.query().filter_by(name=updated_customer).one()
    )
    deleted_order_ = registry.Order.query().filter_by(name=deleted_order).one()
    updated_order_ = registry.Order.query().filter_by(name=updated_order).one()
    unlinked_order_ = (
        registry.Order.query().filter_by(name=unlinked_order).one()
    )
    deleted_tag_ = registry.Tag.query().filter_by(name=deleted_tag).one()
    unlinked_tag_ = registry.Tag.query().filter_by(name=unlinked_tag).one()

    for order in updated_customer_.orders:
        updated_customer_.orders.remove(order)
    updated_customer_.orders.extend(
        [deleted_order_, unlinked_order_, updated_order_]
    )

    for tag in updated_order_.tags:
        updated_order_.tags.remove(tag)
    updated_order_.tags.extend([deleted_tag_, unlinked_tag_])
    registry.flush()

    return registry.FuretUI.CRUD.update(
        "Model.Customer",
        {"id": updated_customer_.id},
        {
            "Model.Customer": {
                f'[["id",{updated_customer_.id}]]': {
                    "name": "Pierre",
                    "orders": [
                        {
                            "__x2m_state": "DELETED",
                            "id": deleted_order_.id,
                        },
                        {
                            "__x2m_state": "UNLINKED",
                            "id": unlinked_order_.id,
                        },
                        {
                            "__x2m_state": "UPDATED",
                            "id": updated_order_.id,
                        },
                    ],
                },
            },
            "Model.Order": {
                f'[["id",{updated_order_.id}]]': {
                    "name": "Order renamed",
                    "tags": [
                        {
                            "__x2m_state": "DELETED",
                            "id": deleted_tag_.id,
                        },
                        {
                            "__x2m_state": "UNLINKED",
                            "id": unlinked_tag_.id,
                        },
                    ],
                }
            },
        },
        "user1",
    )


def test_update_o2m(registry):
    assert update_o2m(registry)


@pytest.mark.parametrize(
    "config,expected_regex_error_message",
    [
        pytest.param(
            {"deleted_order": "Order 2.1"},
            r"You are not allowed to delete this object "
            r"Model.Order\({'id': \d+}\) linked to <Model.Customer\(",
            id="restricted o2m delete team2's tag",
        ),
        pytest.param(
            {"unlinked_order": "Order 2.1"},
            r"You are not allowed to unlink this object "
            r"Model.Order\({'id': \d+}\) linked to <Model.Customer\(",
            id="restricted o2m unlink team2's Order",
        ),
        pytest.param(
            {"deleted_tag": "Tag 2.0"},
            r"You are not allowed to delete this object "
            r"Model.Tag\({'id': \d+}\) linked to <Model.Order\(",
            id="restricted m2m delete team2's tag",
        ),
        pytest.param(
            {"unlinked_tag": "Tag 2.0"},
            r"You are not allowed to unlink this object "
            r"Model.Tag\({'id': \d+}\) linked to <Model.Order\(",
            id="restricted m2m unlink team2's tag",
        ),
    ],
)
def test_restricted_update_o2m(registry, config, expected_regex_error_message):
    with pytest.raises(HTTPForbidden) as ex:
        update_o2m(registry, **config)
    assert re.match(expected_regex_error_message, ex.value.detail)
