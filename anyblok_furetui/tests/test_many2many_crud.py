import pytest

from anyblok import Declarations
from anyblok.column import Integer, String
from anyblok.relationship import Many2Many
from anyblok.tests.conftest import (  # noqa F401
    init_registry_with_bloks,
    reset_db,
    bloks_loaded,
    base_loaded,
)


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

    @register(Model)
    class Building:
        id = Integer(primary_key=True)
        name = String()
        addresses = Many2Many(
            model=Model.Address,
            join_table="join_addresses_building",
            remote_columns="id",
            local_columns="id",
            m2m_remote_columns="a_id",
            m2m_local_columns="b_id",
            many2many="buildings",
        )


@pytest.fixture(scope="class")
def registry_many2many(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(["furetui"], _complete_many2many)
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
        link_address = registry.Address.insert(zip="45270")
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
                                {
                                    "__x2m_state": "LINKED",
                                    "id": link_address.id,
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
                            "buildings": [
                                {
                                    "__x2m_state": "ADDED",
                                    "uuid": "fake_uuid_building",
                                },
                            ],
                        },
                    }
                },
                "Model.Building": {
                    "new": {"fake_uuid_building": {"name": "Bat A."}}
                },
            },
        )

        assert person.name == "Pierre Verkest"
        assert sorted(person.addresses.zip) == [
            "01390",
            "34820",
            link_address.zip,
        ]
        address_34820 = [
            address for address in person.addresses if address.zip == "34820"
        ][0]
        assert len(address_34820.buildings) == 1

    def test_update_m2m(self, registry_many2many):
        registry = registry_many2many

        building = registry.Building.insert(
            name="Building that will be renamed"
        )
        delete_building = registry.Building.insert(name="DELETED BUILDING")
        unchanged_building = registry.Building.insert(name="UNCHANGED BUILDING")
        link_building = registry.Building.insert(name="LINKED BUILDING")
        unlink_building = registry.Building.insert(name="UNLINKED BUILDING")

        address = registry.Address.insert(
            street="14-16 rue soleillet", zip="75020", city="Paris"
        )
        address.buildings.extend(
            [building, delete_building, unchanged_building, unlink_building]
        )

        delete_address = registry.Address.insert(city="DELETED")
        unchanged_address = registry.Address.insert(city="UNCHANGED")
        link_address = registry.Address.insert(city="LINKED")
        unlink_address = registry.Address.insert(city="UNLINKED")

        person = registry.Person.insert(name="Jean-sébastien SUZANNE")
        person.addresses.extend(
            [address, delete_address, unchanged_address, unlink_address]
        )
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
                            {
                                "__x2m_state": "UNLINKED",
                                "id": unlink_address.id,
                            },
                            {"__x2m_state": "LINKED", "id": link_address.id},
                            {"id": unchanged_address.id},
                        ],
                    },
                },
                "Model.Address": {
                    "new": {"fake_uuid_address": {"city": "ADDED"}},
                    '[["id",{}]]'.format(address.id): {
                        "city": "UPDATED",
                        "buildings": [
                            {
                                "__x2m_state": "ADDED",
                                "uuid": "fake_uuid_building",
                            },
                            {"__x2m_state": "UPDATED", "id": building.id},
                            {
                                "__x2m_state": "DELETED",
                                "id": delete_building.id,
                            },
                            {
                                "__x2m_state": "UNLINKED",
                                "id": unlink_building.id,
                            },
                            {"__x2m_state": "LINKED", "id": link_building.id},
                            {"id": unchanged_building.id},
                        ],
                    },
                },
                "Model.Building": {
                    "new": {"fake_uuid_building": {"name": "ADDED BUILDING"}},
                    '[["id",{}]]'.format(building.id): {
                        "name": "UPDATED BUILDING",
                    },
                },
            },
        )
        assert sorted(person.addresses.city) == [
            "ADDED",
            "LINKED",
            "UNCHANGED",
            "UPDATED",
        ]
        assert registry.Address.query().get(delete_address.id) is None
        assert registry.Address.query().get(unlink_address.id) is not None
        address.refresh()
        assert sorted(address.buildings.name) == [
            "ADDED BUILDING",
            "LINKED BUILDING",
            "UNCHANGED BUILDING",
            "UPDATED BUILDING",
        ]
        assert registry.Building.query().get(delete_building.id) is None
        assert registry.Building.query().get(unlink_building.id) is not None
