import pytest
import urllib
from anyblok.config import Configuration
from anyblok.blok import BlokManager
from os.path import join


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
                    "data": {"label": "Tag 1", "list": {"id": resource_list.id}},
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
        self, webserver, rollback_registry, resource_list, resource_tag1, resource_tag2
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
                        "tags": [{"id": resource_tag1.id}, {"id": resource_tag2.id}],
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
