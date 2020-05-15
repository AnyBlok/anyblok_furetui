import json
import pytest
import urllib


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


@pytest.fixture(scope="function")
def resource_tag5(rollback_registry, resource_list):
    return rollback_registry.FuretUI.Resource.Tags.insert(
        key="tag-5", label="Tag 5", list=resource_list
    )


@pytest.fixture(scope="function")
def resource_tag_to_link(rollback_registry, resource_list):
    return rollback_registry.FuretUI.Resource.Tags.insert(
        key="tag-6", label="Tag 6"
    )


@pytest.mark.usefixtures("rollback_registry")
class TestCreate:

    @pytest.fixture(autouse=True)
    def transact(self, request, rollback_registry, webserver):
        rollback_registry.Pyramid.User.insert(login='test')
        rollback_registry.Pyramid.CredentialStore.insert(
            login='test', password='test')
        webserver.post_json(
            '/furet-ui/login', {'login': 'test', 'password': 'test'},
            status=200)

        def logout():
            webserver.post_json('/furet-ui/logout', status=200)

        request.addfinalizer(logout)

    def test_create(self, webserver, rollback_registry):
        title = "test-create-blok-list-resource"
        path = "/furet-ui/resource/0/crud"
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

    def test_unauthenticated_create(self, webserver, rollback_registry):
        title = "test-create-blok-list-resource"
        webserver.post_json('/furet-ui/logout', status=200)
        path = "/furet-ui/resource/0/crud"
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
        webserver.post(path, payload, headers=headers, status=405)

    def test_create_o2m(
        self, rollback_registry, resource_tag_to_link
    ):
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
                                {
                                    "__x2m_state": "LINKED",
                                    "id": resource_tag_to_link.id,
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
        assert len(new_list.tags) == 3
        assert new_list.tags.key == [
            tag_key1,
            tag_key2,
            resource_tag_to_link.key,
        ]


@pytest.mark.usefixtures("rollback_registry")
class TestRead:

    @pytest.fixture(autouse=True)
    def transact(self, request, rollback_registry, webserver):
        rollback_registry.Pyramid.User.insert(login='test')
        rollback_registry.Pyramid.CredentialStore.insert(
            login='test', password='test')
        webserver.post_json(
            '/furet-ui/login', {'login': 'test', 'password': 'test'},
            status=200)

        def logout():
            webserver.post_json('/furet-ui/logout', status=200)

        request.addfinalizer(logout)

    def test_unauthenticated(self, webserver, rollback_registry):
        path = "/furet-ui/resource/0/crud"
        webserver.post_json('/furet-ui/logout', status=200)
        params = urllib.parse.urlencode(
            {
                "context[model]": "Model.System.Blok",
                "context[fields]": "name,author",
                "filter[name][eq]": "anyblok-core",
            }
        )
        webserver.get(path, params, status=405)

    def test_model_field(self, webserver, rollback_registry):
        path = "/furet-ui/resource/0/crud"
        params = urllib.parse.urlencode(
            {
                "context[model]": "Model.System.Blok",
                "context[fields]": "name,author",
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

    def test_o2m_field(
        self,
        webserver,
        rollback_registry,
        resource_list,
        resource_tag1,
        resource_tag2,
    ):
        path = "/furet-ui/resource/0/crud"
        params = urllib.parse.urlencode(
            {
                "context[model]": "Model.FuretUI.Resource.List",
                "context[fields]": "title,tags.label",
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
        path = "/furet-ui/resource/0/crud"
        params = urllib.parse.urlencode(
            {
                "context[model]": "Model.System.Model",
                "context[fields]": "name,table",
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

    @pytest.fixture(autouse=True)
    def transact(self, request, rollback_registry, webserver):
        rollback_registry.Pyramid.User.insert(login='test')
        rollback_registry.Pyramid.CredentialStore.insert(
            login='test', password='test')
        webserver.post_json(
            '/furet-ui/login', {'login': 'test', 'password': 'test'},
            status=200)

        def logout():
            webserver.post_json('/furet-ui/logout', status=200)

        request.addfinalizer(logout)

    def test_update(self, webserver, rollback_registry, resource_list):
        title = "test-update-list-resource"
        path = "/furet-ui/resource/0/crud"
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

    def test_unauthenticated_update(self, webserver, rollback_registry,
                                    resource_list):
        title = "test-update-list-resource"
        webserver.post_json('/furet-ui/logout', status=200)
        path = "/furet-ui/resource/0/crud"
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
        webserver.patch(path, params, headers, status=405)

    def test_update_o2m(
        self,
        webserver,
        rollback_registry,
        resource_tag1,
        resource_tag2,
        resource_tag3,
        resource_tag4,
        resource_tag5,
        resource_tag_to_link,
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
                            {"__x2m_state": "UNLINKED", "id": resource_tag5.id},
                            {
                                "__x2m_state": "LINKED",
                                "id": resource_tag_to_link.id,
                            },
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
        assert len(new_list.tags) == 6
        assert sorted(new_list.tags.key) == sorted(
            [
                tag_key_update_1,
                tag_key1,
                tag_key2,
                resource_tag3.key,
                resource_tag4.key,
                resource_tag_to_link.key,
            ]
        )
        assert (
            rollback_registry.FuretUI.Resource.Tags.query().get(
                resource_tag2.id
            )
            is None
        )
        assert (
            rollback_registry.FuretUI.Resource.Tags.query().get(
                resource_tag5.id
            )
            is not None
        )


@pytest.mark.usefixtures("rollback_registry")
class TestDelete:

    @pytest.fixture(autouse=True)
    def transact(self, request, rollback_registry, webserver):
        rollback_registry.Pyramid.User.insert(login='test')
        rollback_registry.Pyramid.CredentialStore.insert(
            login='test', password='test')
        webserver.post_json(
            '/furet-ui/login', {'login': 'test', 'password': 'test'},
            status=200)

        def logout():
            webserver.post_json('/furet-ui/logout', status=200)

        request.addfinalizer(logout)

    def test_delete(self, webserver, rollback_registry, resource_list):
        path = "/furet-ui/resource/0/crud"
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

    def test_unauhenticated_delete(self, webserver, rollback_registry,
                                   resource_list):
        path = "/furet-ui/resource/0/crud"
        webserver.post_json('/furet-ui/logout', status=200)
        params = urllib.parse.urlencode(
            {
                "model": "Model.FuretUI.Resource.List",
                "pks": json.dumps({"id": resource_list.id}),
            }
        )
        webserver.delete(path, params, status=405)
