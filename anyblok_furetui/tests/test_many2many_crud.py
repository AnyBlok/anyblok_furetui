import pytest

from anyblok import Declarations
from anyblok.column import Integer, String
from anyblok.relationship import Many2Many
from anyblok.tests.conftest import (  # noqa F401
    init_registry,
    reset_db,
    bloks_loaded,
    base_loaded,
)
from anyblok.conftest import configuration_loaded  # noqa F401


register = Declarations.register
Model = Declarations.Model


def _complete_many2many(**kwargs):
    @register(Model)
    class Address:

        id = Integer(primary_key=True)
        street = String()
        zip = String()
        city = String()

    @register(Model)
    class Person:

        name = String(primary_key=True)
        addresses = Many2Many(
            model=Model.Address,
            join_table="join_addresses_by_persons",
            remote_columns="id",
            local_columns="name",
            m2m_remote_columns="a_id",
            m2m_local_columns="p_name",
            many2many="persons",
        )


@pytest.fixture(scope="class")
def registry_many2many(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry(_complete_many2many)
    request.addfinalizer(registry.close)
    return registry


class TestMany2Many:
    @pytest.fixture(autouse=True)
    def transact(self, request, registry_many2many):
        transaction = registry_many2many.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_create_m2m(self, registry_many2many):
        registry = registry_many2many
        person = registry.FuretUI.CRUD.create(
            "Model.Person",
            "fake_uuid_person",
            {
                "Model.Person": {
                    "new": {
                        "fake_uuid_person": {
                            "name": "Pierre Verkest",
                            "addresses": [
                                {
                                    "__x2m_state": "ADDED",
                                    "uuid": "fake_uuid_address1",
                                },
                                {
                                    "__x2m_state": "ADDED",
                                    "uuid": "fake_uuid_address2",
                                },
                            ],
                        },
                    }
                },
                "Model.Address": {
                    "new": {
                        "fake_uuid_address1": {
                            "street": "RUE DU MARQUIS DE SALLMARD",
                            "zip": "01390",
                            "city": "TRAMOYES",
                        },
                        "fake_uuid_address2": {
                            "street": "IMPASSE DES PINS",
                            "zip": "34820",
                            "city": "TEYRAN",
                        },
                    }
                },
            },
        )

        assert person.name == "Pierre Verkest"
        assert sorted(person.addresses.zip) == ["01390", "34820"]

    def test_update_m2m(self, registry_many2many):
        registry = registry_many2many

        address = registry.Address.insert(
            street="14-16 rue soleillet", zip="75020", city="Paris"
        )
        delete_address = registry.Address.insert(city="DELETED")
        unchanged_address = registry.Address.insert(city="UNCHANGED")
        person = registry.Person.insert(name="Jean-sébastien SUZANNE")
        person.addresses.extend([address, delete_address, unchanged_address])

        registry.FuretUI.CRUD.update(
            "Model.Person",
            {"name": person.name},
            {
                "Model.Person": {
                    '[["name","{}"]]'.format(person.name): {
                        "addresses": [
                            {
                                "__x2m_state": "ADDED",
                                "uuid": "fake_uuid_address",
                            },
                            {"__x2m_state": "UPDATED", "id": address.id},
                            {"__x2m_state": "DELETED", "id": delete_address.id},
                            {"id": unchanged_address.id},
                        ],
                    },
                },
                "Model.Address": {
                    "new": {"fake_uuid_address": {"city": "ADDED"}},
                    '[["id",{}]]'.format(address.id): {"city": "UPDATED"},
                },
            },
        )
        assert sorted(person.addresses.city) == [
            "ADDED",
            "UNCHANGED",
            "UPDATED",
        ]
        assert registry.Address.query().get(delete_address.id) is None
