import pytest
from anyblok import Declarations
from anyblok.column import Integer, String
from anyblok.relationship import Many2One, One2Many
from anyblok.tests.conftest import (base_loaded, bloks_loaded,  # noqa F401
                                    init_registry_with_bloks, reset_db)
from sqlalchemy import ForeignKeyConstraint

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


def required_many2one_with_one2many_multi_primary_key(**kwargs):
    @register(Model)
    class Order:
        uuid = Integer(primary_key=True)
        name = String(primary_key=True)

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


def one2many_with_required_fk_and_multi_primary_key(**kwargs):  # noqa F811
    primaryjoin = (
        "ModelOrder.uuid == ModelLine.order_id and "
        "ModelOrder.name == ModelLine.order_name"
    )

    @register(Model)
    class Order:
        uuid = Integer(primary_key=True)
        name = String(primary_key=True)
        lines = One2Many(model='Model.Line',
                         remote_columns=["order_id", "order_name"],
                         primaryjoin=primaryjoin)

    @register(Model)
    class Line:

        uuid = Integer(primary_key=True)
        order_id = Integer(nullable=False)
        order_name = String(nullable=False)
        name = String()

        @classmethod
        def define_table_args(cls):
            table_args = super(Line, cls).define_table_args()
            Order = cls.registry.Order
            return table_args + (ForeignKeyConstraint(
                [cls.order_id, cls.order_name], [Order.uuid, Order.name],
                ondelete="CASCADE"),)


@pytest.fixture(
    scope="class",
    params=[
        many2one_with_one2many,
        required_many2one_with_one2many,
        required_many2one_with_one2many_multi_primary_key,
        one2many_and_many2one,
        one2many,
        one2many_with_required_fk,
        one2many_with_required_fk_and_multi_primary_key,
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
            "fakeuser",
        )

        assert order.name == "Order One"
        assert sorted(order.lines.name) == [
            "Line 1",
            "Line 2",
        ]
