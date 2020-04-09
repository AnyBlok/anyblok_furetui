import json
import pytest
import urllib
from anyblok.config import Configuration


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


@pytest.fixture(scope="function")
def resource_list(rollback_registry):
    return rollback_registry.FuretUI.Resource.List.insert(
        title="test-blok", model="Model.System.Blok"
    )


@pytest.fixture(scope="function")
def resource_tag1(rollback_registry, resource_list):
    return rollback_registry.FuretUI.Resource.Tags.insert(
        key="tag-1", label="Tag 1", list=resource_list
    )


@pytest.fixture(scope="function")
def resource_tag2(rollback_registry, resource_list):
    return rollback_registry.FuretUI.Resource.Tags.insert(
        key="tag-2", label="Tag 2", list=resource_list
    )


@pytest.fixture(scope="function")
def resource_tag3(rollback_registry, resource_list):
    return rollback_registry.FuretUI.Resource.Tags.insert(
        key="tag-3", label="Tag 3", list=resource_list
    )


@pytest.fixture(scope="function")
def resource_tag4(rollback_registry, resource_list):
    return rollback_registry.FuretUI.Resource.Tags.insert(
        key="tag-4", label="Tag 4", list=resource_list
    )


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


@pytest.mark.usefixtures("rollback_registry")
class TestCreate:
    def test_create(self, webserver, rollback_registry):
        title = "test-create-blok-list-resource"
        path = Configuration.get("furetui_client_path", "/furet-ui/crud")
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = json.dumps(
            {
                "changes": {
                    "Model.FuretUI.Resource.List": {
                        "new": {
                            "fake_uuid": {
                                "title": title,
                                "model": "Model.System.Blok",
                            }
                        }
                    }
                },
                "model": "Model.FuretUI.Resource.List",
                "uuid": "fake_uuid",
            }
        )
        response = webserver.post(path, payload, headers=headers)
        assert response.status_code == 200
        rollback_registry.FuretUI.Resource.List.query().filter_by(
            title=title
        ).count() == 1

    def test_create_o2m(self, webserver, rollback_registry):
        tag_key1 = "key1-create-o2m"
        tag_key2 = "key2-create-o2m"
        list_title = "new-title"
        new_list_obj = rollback_registry.FuretUI.CRUD.create(
            "Model.FuretUI.Resource.List",
            "fake_uuid_list",
            {
                "Model.FuretUI.Resource.Tags": {
                    "new": {
                        "fake_uuid_tag1": {
                            "key": tag_key1,
                            "label": "Key created in o2m",
                        },
                        "fake_uuid_tag2": {
                            "key": tag_key2,
                            "label": "Key created in o2m",
                        },
                    }
                },
                "Model.FuretUI.Resource.List": {
                    "new": {
                        "fake_uuid_list": {
                            "title": list_title,
                            "model": "Model.System.Blok",
                            "tags": [
                                {
                                    "__x2m_state": "ADDED",
                                    "uuid": "fake_uuid_tag1",
                                },
                                {
                                    "__x2m_state": "ADDED",
                                    "uuid": "fake_uuid_tag2",
                                },
                            ],
                        }
                    }
                },
            },
        )
        new_list = (
            rollback_registry.FuretUI.Resource.List.query()
            .filter_by(title=list_title)
            .one()
        )
        assert new_list.id == new_list_obj.id
        assert len(new_list.tags) == 2
        assert new_list.tags.key == [tag_key1, tag_key2]


@pytest.mark.usefixtures("rollback_registry")
class TestRead:
    def test_model_field(self, webserver, rollback_registry):
        path = Configuration.get("furetui_client_path", "/furet-ui/crud")
        params = urllib.parse.urlencode(
            {
                "model": "Model.System.Blok",
                "fields": "name,author",
                "filter[name][eq]": "anyblok-core",
            }
        )
        response = webserver.get(path, params)
        assert response.status_code == 200
        assert response.json == {
            "data": [
                {
                    "data": {
                        "author": "Suzanne Jean-Sébastien",
                        "name": "anyblok-core",
                    },
                    "model": "Model.System.Blok",
                    "pk": {"name": "anyblok-core"},
                    "type": "UPDATE_DATA",
                }
            ],
            "pks": [{"name": "anyblok-core"}],
            "total": 1,
        }

    def test_m2o_field(
        self, webserver, rollback_registry, resource_list, resource_tag1
    ):
        path = Configuration.get("furetui_client_path", "/furet-ui/crud")
        params = urllib.parse.urlencode(
            {
                "model": "Model.FuretUI.Resource.Tags",
                "fields": "label,list.title",
                "filter[key][eq]": "tag-1",
            }
        )
        response = webserver.get(path, params)
        assert response.status_code == 200
        assert response.json == {
            "data": [
                {
                    "data": {
                        "label": "Tag 1",
                        "list": {"id": resource_list.id},
                    },
                    "model": "Model.FuretUI.Resource.Tags",
                    "pk": {"id": resource_tag1.id},
                    "type": "UPDATE_DATA",
                },
                {
                    "data": {"title": "test-blok"},
                    "model": "Model.FuretUI.Resource.List",
                    "pk": {"id": resource_list.id},
                    "type": "UPDATE_DATA",
                },
            ],
            "pks": [{"id": resource_tag1.id}],
            "total": 1,
        }

    def test_o2m_field(
        self,
        webserver,
        rollback_registry,
        resource_list,
        resource_tag1,
        resource_tag2,
    ):
        path = Configuration.get("furetui_client_path", "/furet-ui/crud")
        params = urllib.parse.urlencode(
            {
                "model": "Model.FuretUI.Resource.List",
                "fields": "title,tags.label",
                "filter[title][eq]": "test-blok",
            }
        )
        response = webserver.get(path, params)
        assert response.status_code == 200
        assert response.json == {
            "data": [
                {
                    "data": {
                        "tags": [
                            {"id": resource_tag1.id},
                            {"id": resource_tag2.id},
                        ],
                        "title": "test-blok",
                    },
                    "model": "Model.FuretUI.Resource.List",
                    "pk": {"id": resource_list.id},
                    "type": "UPDATE_DATA",
                },
                {
                    "data": {"label": "Tag 1"},
                    "model": "Model.FuretUI.Resource.Tags",
                    "pk": {"id": resource_tag1.id},
                    "type": "UPDATE_DATA",
                },
                {
                    "data": {"label": "Tag 2"},
                    "model": "Model.FuretUI.Resource.Tags",
                    "pk": {"id": resource_tag2.id},
                    "type": "UPDATE_DATA",
                },
            ],
            "pks": [{"id": resource_list.id}],
            "total": 1,
        }

    def test_limit_offset_order_exclude(self, webserver, rollback_registry):
        path = Configuration.get("furetui_client_path", "/furet-ui/crud")
        params = urllib.parse.urlencode(
            {
                "model": "Model.System.Model",
                "fields": "name,table",
                "~filter[is_sql_model][eq]": False,
                "filter[table][like]": "system_",
                "order_by[name]": "asc",
                "order_by[table]": "desc",
                "limit": 2,
                "offset": 2,
            }
        )
        response = webserver.get(path, params)
        assert response.status_code == 200
        # Writing this test System SQL table are::
        #
        #  Model.System.Blok                      | system_blok
        #  Model.System.Cache                     | system_cache
        #  Model.System.Column                    | system_column
        #  Model.System.Field                     | system_field
        #  Model.System.Model                     | system_model
        #  Model.System.Parameter                 | system_parameter
        #  Model.System.RelationShip              | system_relationship
        #  Model.System.Sequence                  | system_sequence
        assert response.json == {
            "data": [
                {
                    "data": {
                        "name": "Model.System.Column",
                        "table": "system_column",
                    },
                    "model": "Model.System.Model",
                    "pk": {"name": "Model.System.Column"},
                    "type": "UPDATE_DATA",
                },
                {
                    "data": {
                        "name": "Model.System.Field",
                        "table": "system_field",
                    },
                    "model": "Model.System.Model",
                    "pk": {"name": "Model.System.Field"},
                    "type": "UPDATE_DATA",
                },
            ],
            "pks": [
                {"name": "Model.System.Column"},
                {"name": "Model.System.Field"},
            ],
            "total": 8,
        }


@pytest.mark.usefixtures("rollback_registry")
class TestUpdate:
    def test_update(self, webserver, rollback_registry, resource_list):
        title = "test-update-list-resource"
        path = Configuration.get("furetui_client_path", "/furet-ui/crud")
        formated_record_id = '[["id",{}]]'.format(resource_list.id)
        headers = {"Content-Type": "application/json; charset=utf-8"}
        params = json.dumps(
            {
                "changes": {
                    "Model.FuretUI.Resource.List": {
                        formated_record_id: {"title": title}
                    }
                },
                "model": "Model.FuretUI.Resource.List",
                "pks": {"id": resource_list.id},
            }
        )
        response = webserver.patch(path, params, headers)
        assert response.status_code == 200
        assert (
            rollback_registry.FuretUI.Resource.List.query()
            .filter_by(title=title)
            .one()
            .id
            == resource_list.id
        )

    def test_update_o2m(
        self,
        webserver,
        rollback_registry,
        resource_tag1,
        resource_tag2,
        resource_tag3,
        resource_tag4,
    ):
        tag_key_update_1 = "key1-update_o2m_updated"
        tag_key1 = "key1-update_o2m_added"
        tag_key2 = "key2-update_o2m_added"

        rollback_registry.FuretUI.CRUD.update(
            "Model.FuretUI.Resource.List",
            {"id": resource_tag1.list.id},
            {
                "Model.FuretUI.Resource.Tags": {
                    "new": {
                        "fake_uuid_tag1": {
                            "key": tag_key1,
                            "label": "Key created in o2m",
                        },
                        "fake_uuid_tag2": {
                            "key": tag_key2,
                            "label": "Key created in o2m",
                        },
                    },
                    '[["id",{}]]'.format(resource_tag1.id): {
                        "key": tag_key_update_1,
                    },
                },
                "Model.FuretUI.Resource.List": {
                    '[["id",{}]]'.format(resource_tag1.list.id): {
                        "tags": [
                            {"__x2m_state": "ADDED", "uuid": "fake_uuid_tag1"},
                            {"__x2m_state": "ADDED", "uuid": "fake_uuid_tag2"},
                            {"__x2m_state": "UPDATED", "id": resource_tag1.id},
                            {"__x2m_state": "DELETED", "id": resource_tag2.id},
                            {"id": resource_tag3.id},
                        ],
                    }
                },
            },
        )
        new_list = (
            rollback_registry.FuretUI.Resource.List.query()
            .filter_by(title=resource_tag1.list.title)
            .one()
        )
        assert len(new_list.tags) == 5
        assert sorted(new_list.tags.key) == sorted(
            [
                tag_key_update_1,
                tag_key1,
                tag_key2,
                resource_tag3.key,
                resource_tag4.key,
            ]
        )


@pytest.mark.usefixtures("rollback_registry")
class TestDelete:
    def test_delete(self, webserver, rollback_registry, resource_list):
        path = Configuration.get("furetui_client_path", "/furet-ui/crud")
        params = urllib.parse.urlencode(
            {
                "model": "Model.FuretUI.Resource.List",
                "pks": json.dumps({"id": resource_list.id}),
            }
        )
        response = webserver.delete(path, params)
        assert response.status_code == 200
        assert (
            rollback_registry.FuretUI.Resource.List.query()
            .filter_by(title=resource_list.title)
            .count()
            == 0
        )
