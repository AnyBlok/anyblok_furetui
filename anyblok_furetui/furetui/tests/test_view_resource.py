import pytest


@pytest.mark.usefixtures('rollback_registry')
class TestViewResource:

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

    def test_get_resource(self, webserver, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.Custom.insert(
            component='test')
        response = webserver.get(f'/furet-ui/resource/{resource.id}')
        assert response.json_body == [
            {
                'definitions': [
                    {
                        'code': None,
                        'component': 'test',
                        'id': resource.id,
                        'type': 'custom'
                    }
                ],
                'type': 'UPDATE_RESOURCES'
            },
        ]

    def test_open_resource(self, webserver, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.Custom.insert(
            component='test')
        rollback_registry.IO.Mapping.set('tmp_resource', resource)
        response = webserver.post_json(
            '/furet-ui/open/resource/tmp_resource',
            {
                'params': {},
                'route': 'route_name',
            }
        )
        assert response.json_body == [
            {
                'definitions': [
                    {
                        'code': None,
                        'component': 'test',
                        'id': resource.id,
                        'type': 'custom'
                    }
                ],
                'type': 'UPDATE_RESOURCES'
            },
            {
                'name': 'route_name',
                'params': {'id': resource.id},
                'query': '',
                'type': 'UPDATE_ROUTE'
            }
        ]

    def test_open_resource_without_mapping(self, webserver, rollback_registry):
        webserver.post_json(
            '/furet-ui/open/resource/tmp_resource',
            {'params': {}, 'route': 'route_name'},
            status=500
        )
