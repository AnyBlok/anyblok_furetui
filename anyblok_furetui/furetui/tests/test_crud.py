import json
import pytest
import urllib
from anyblok.config import Configuration


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

    def test_update_m2o(self):
        pytest.fail("not implemented")

    def test_update_o2m(self):
        pytest.fail("not implemented")


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
