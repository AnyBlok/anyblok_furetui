import pytest

from anyblok import Declarations
from anyblok.column import Integer, String
from anyblok.relationship import Many2One, One2Many
from anyblok.tests.conftest import (  # noqa F401
    init_registry_with_bloks,
    reset_db,
    bloks_loaded,
    base_loaded,
)


register = Declarations.register
Model = Declarations.Model

primaryjoin = "ModelOrder.uuid == ModelLine.order_id"


def many2one_with_one2many(**kwargs):
    @register(Model)
    class Order:
        uuid = Integer(primary_key=True)
        name = String()

    @register(Model)
    class Line:

        uuid = Integer(primary_key=True)
        order = Many2One(model=Model.Order,
                         one2many="lines")
        name = String()


def required_many2one_with_one2many(**kwargs):
    @register(Model)
    class Order:
        uuid = Integer(primary_key=True)
        name = String()

    @register(Model)
    class Line:

        uuid = Integer(primary_key=True)
        order = Many2One(model=Model.Order,
                         nullable=False,
                         one2many="lines")
        name = String()


def one2many_and_many2one(**kwargs):
    @register(Model)
    class Order:
        uuid = Integer(primary_key=True)
        name = String()
        lines = One2Many(model='Model.Line',
                         remote_columns="order_id",
                         primaryjoin=primaryjoin,
                         many2one="order")

    @register(Model)
    class Line:

        uuid = Integer(primary_key=True)
        order_id = Integer(foreign_key=Model.Order.use('uuid'))
        name = String()


def one2many(**kwargs):
    @register(Model)
    class Order:
        uuid = Integer(primary_key=True)
        name = String()
        lines = One2Many(model='Model.Line',
                         remote_columns="order_id",
                         primaryjoin=primaryjoin)

    @register(Model)
    class Line:

        uuid = Integer(primary_key=True)
        order_id = Integer(foreign_key=Model.Order.use('uuid'))
        name = String()


def one2many_with_required_fk(**kwargs):  # noqa F811
    @register(Model)
    class Order:
        uuid = Integer(primary_key=True)
        name = String()
        lines = One2Many(model='Model.Line',
                         remote_columns="order_id",
                         primaryjoin=primaryjoin)

    @register(Model)
    class Line:

        uuid = Integer(primary_key=True)
        order_id = Integer(foreign_key=Model.Order.use('uuid'),
                           nullable=False)
        name = String()


@pytest.fixture(
    scope="class",
    params=[
        many2one_with_one2many,
        required_many2one_with_one2many,
        one2many_and_many2one,
        one2many,
        one2many_with_required_fk,
    ]
)
def registry_one2many(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(["furetui"], request.param)
    request.addfinalizer(registry.close)
    return registry


class Testone2many:
    @pytest.fixture(autouse=True)
    def transact(self, request, registry_one2many):
        transaction = registry_one2many.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_create_o2m_with_required_m2o(self, registry_one2many):
        registry = registry_one2many
        order = registry.FuretUI.CRUD.create(
            "Model.Order",
            "fake_uuid_order",
            {
                "Model.Order": {
                    "new": {
                        "fake_uuid_order": {
                            "name": "Order One",
                            "lines": [
                                {
                                    "__x2m_state": "ADDED",
                                    "uuid": "fake_uuid_line_1",
                                },
                                {
                                    "__x2m_state": "ADDED",
                                    "uuid": "fake_uuid_line_2",
                                },
                            ],
                        },
                    }
                },
                "Model.Line": {
                    "new": {
                        "fake_uuid_line_1": {
                            "name": "Line 1",
                        },
                        "fake_uuid_line_2": {
                            "name": "Line 2",
                        },
                    }
                },
            },
        )

        assert order.name == "Order One"
        assert sorted(order.lines.name) == [
            "Line 1",
            "Line 2",
        ]
