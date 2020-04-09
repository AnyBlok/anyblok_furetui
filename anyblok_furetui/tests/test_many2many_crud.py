import pytest

from pyramid.request import Request
from urllib.parse import urlencode

from anyblok import Declarations
from anyblok.column import Integer, String
from anyblok.relationship import Many2Many, Many2One
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
    class Building:
        id = Integer(primary_key=True)
        name = String()

    @register(Model)
    class Address:

        id = Integer(primary_key=True)
        main_building = Many2One(model=Model.Building)
        buildings = Many2Many(
            model=Model.Building,
            join_table="join_addresses_buildings",
            remote_columns="id",
            local_columns="id",
            m2m_remote_columns="b_id",
            m2m_local_columns="a_id",
            many2many="addresses",
        )
        street = String()
        zip = String()
        city = String()

    @register(Model)
    class Person:

        name = String(primary_key=True)
        main_address = Many2One(model=Model.Address)
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
    registry = init_registry_with_bloks(["furetui"], _complete_many2many)
    request.addfinalizer(registry.close)
    return registry


class TestMany2Many:
    @pytest.fixture(autouse=True)
    def transact(self, request, registry_many2many):
        transaction = registry_many2many.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    @pytest.fixture()
    def setup_data(self, registry_many2many):
        registry = registry_many2many
        self.building = registry.Building.insert(
            name="Building that will be renamed"
        )
        self.delete_building = registry.Building.insert(name="DELETED BUILDING")
        self.unchanged_building = registry.Building.insert(
            name="UNCHANGED BUILDING"
        )
        self.link_building = registry.Building.insert(name="LINKED BUILDING")
        self.unlink_building = registry.Building.insert(
            name="UNLINKED BUILDING"
        )

        self.address = registry.Address.insert(
            street="14-16 rue soleillet",
            zip="75020",
            city="Paris",
            main_building=self.building,
        )
        self.address.buildings.extend(
            [
                self.building,
                self.delete_building,
                self.unchanged_building,
                self.unlink_building,
            ]
        )

        self.delete_address = registry.Address.insert(
            city="DELETED", zip="89666"
        )
        self.unchanged_address = registry.Address.insert(
            city="UNCHANGED", zip="89666"
        )
        self.link_address = registry.Address.insert(city="LINKED", zip="89666")
        self.unlink_address = registry.Address.insert(
            city="UNLINKED", zip="89666"
        )

        self.person = registry.Person.insert(
            name="Jean-sébastien SUZANNE", main_address=self.address
        )
        self.person.addresses.extend(
            [
                self.address,
                self.delete_address,
                self.unchanged_address,
                self.unlink_address,
            ]
        )

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

    def test_read(self, registry_many2many, setup_data):
        registry = registry_many2many
        read = registry.FuretUI.CRUD.read(
            Request(
                {
                    "QUERY_STRING": urlencode(
                        query={
                            "model": "Model.Person",
                            "fields": "name,main_address.city,"
                            "main_address.zip,addresses.zip",
                        }
                    )
                }
            )
        )

        assert read == {
            "data": [
                {
                    "data": {
                        "addresses": [
                            {"id": self.address.id},
                            {"id": self.delete_address.id},
                            {"id": self.unchanged_address.id},
                            {"id": self.unlink_address.id},
                        ],
                        "main_address": {"id": self.address.id},
                        "name": "Jean-sébastien SUZANNE",
                    },
                    "model": "Model.Person",
                    "pk": {"name": "Jean-sébastien SUZANNE"},
                    "type": "UPDATE_DATA",
                },
                {
                    "data": {"city": "Paris", "zip": "75020"},
                    "model": "Model.Address",
                    "pk": {"id": self.address.id},
                    "type": "UPDATE_DATA",
                },
                {
                    "data": {"zip": "75020"},
                    "model": "Model.Address",
                    "pk": {"id": self.address.id},
                    "type": "UPDATE_DATA",
                },
                {
                    "data": {"zip": "89666"},
                    "model": "Model.Address",
                    "pk": {"id": self.delete_address.id},
                    "type": "UPDATE_DATA",
                },
                {
                    "data": {"zip": "89666"},
                    "model": "Model.Address",
                    "pk": {"id": self.unchanged_address.id},
                    "type": "UPDATE_DATA",
                },
                {
                    "data": {"zip": "89666"},
                    "model": "Model.Address",
                    "pk": {"id": self.unlink_address.id},
                    "type": "UPDATE_DATA",
                },
            ],
            "pks": [{"name": "Jean-sébastien SUZANNE"}],
            "total": 1,
        }

    def test_update_m2m(self, registry_many2many, setup_data):
        registry = registry_many2many
        registry.FuretUI.CRUD.update(
            "Model.Person",
            {"name": self.person.name},
            {
                "Model.Person": {
                    '[["name","{}"]]'.format(self.person.name): {
                        "addresses": [
                            {
                                "__x2m_state": "ADDED",
                                "uuid": "fake_uuid_address",
                            },
                            {"__x2m_state": "UPDATED", "id": self.address.id},
                            {
                                "__x2m_state": "DELETED",
                                "id": self.delete_address.id,
                            },
                            {
                                "__x2m_state": "UNLINKED",
                                "id": self.unlink_address.id,
                            },
                            {
                                "__x2m_state": "LINKED",
                                "id": self.link_address.id,
                            },
                            {"id": self.unchanged_address.id},
                        ],
                    },
                },
                "Model.Address": {
                    "new": {"fake_uuid_address": {"city": "ADDED"}},
                    '[["id",{}]]'.format(self.address.id): {
                        "city": "UPDATED",
                        "buildings": [
                            {
                                "__x2m_state": "ADDED",
                                "uuid": "fake_uuid_building",
                            },
                            {"__x2m_state": "UPDATED", "id": self.building.id},
                            {
                                "__x2m_state": "DELETED",
                                "id": self.delete_building.id,
                            },
                            {
                                "__x2m_state": "UNLINKED",
                                "id": self.unlink_building.id,
                            },
                            {
                                "__x2m_state": "LINKED",
                                "id": self.link_building.id,
                            },
                            {"id": self.unchanged_building.id},
                        ],
                    },
                },
                "Model.Building": {
                    "new": {"fake_uuid_building": {"name": "ADDED BUILDING"}},
                    '[["id",{}]]'.format(self.building.id): {
                        "name": "UPDATED BUILDING",
                    },
                },
            },
        )
        assert sorted(self.person.addresses.city) == [
            "ADDED",
            "LINKED",
            "UNCHANGED",
            "UPDATED",
        ]
        assert registry.Address.query().get(self.delete_address.id) is None
        assert registry.Address.query().get(self.unlink_address.id) is not None
        self.address.refresh()
        assert sorted(self.address.buildings.name) == [
            "ADDED BUILDING",
            "LINKED BUILDING",
            "UNCHANGED BUILDING",
            "UPDATED BUILDING",
        ]
        assert registry.Building.query().get(self.delete_building.id) is None
        assert (
            registry.Building.query().get(self.unlink_building.id) is not None
        )
