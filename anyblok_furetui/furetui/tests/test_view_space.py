import pytest


@pytest.mark.usefixtures('rollback_registry')
class TestViewSpace:

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

    def import_space_definition(self, registry):
        resource = registry.FuretUI.Resource.Custom.insert(component='test')
        Menu = registry.FuretUI.Menu
        space = registry.FuretUI.Space.insert(
            code="test", label="Test", description="Test")

        root = Menu.Root.insert(label="Root", space=space)
        menu = Menu.Resource.insert(label="Resource 1", resource=resource,
                                    parent_id=root.id)
        return (space.code, menu.id, resource.id)

    def test_get_spaces(self, webserver, rollback_registry):
        (space, menu, resource) = self.import_space_definition(
            rollback_registry)
        response = webserver.get('/furet-ui/spaces')
        assert response.json_body == [
            {
                'menus': [
                    {
                        'code': 'test',
                        'description': 'Test',
                        'icon': {
                            'code': None,
                            'type': None
                        },
                        'label': 'Test',
                        'path': (
                            f'/space/{space}/menu/{menu}/resource/{resource}?'
                        )
                    }
                ],
                'type': 'UPDATE_SPACE_MENUS'
            },
        ]

    def test_get_space(self, webserver, rollback_registry):
        (space, menu, resource) = self.import_space_definition(
            rollback_registry)
        m = rollback_registry.FuretUI.Menu.query().get(menu)
        response = webserver.get(f'/furet-ui/space/{space}')
        assert response.json_body == [
            {
                'label': 'Test',
                'type': 'UPDATE_CURRENT_SPACE'
            },
            {
                'menus': [
                    {
                        'children': [
                            {
                                'children': [],
                                'filters': {},
                                'icon_code': None,
                                'icon_type': None,
                                'id': menu,
                                'label': 'Resource 1',
                                'order': 100,
                                'order_by': None,
                                'resource': resource,
                                'tags': None
                            }
                        ],
                        'icon_code': None,
                        'icon_type': None,
                        'id': m.parent_id,
                        'label': 'Root',
                        'order': 100
                    }
                ],
                'type': 'UPDATE_CURRENT_LEFT_MENUS'
            },
        ]
