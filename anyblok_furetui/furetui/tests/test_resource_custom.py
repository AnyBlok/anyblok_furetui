import pytest


@pytest.mark.usefixtures('rollback_registry')
class TestResourceCustom:

    def test_get_definition(self, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.Custom.insert(
            code='test-custom-resource', component='test-custom-resource')
        assert resource.get_definitions() == [{
            'code': 'test-custom-resource',
            'component': 'test-custom-resource',
            'id': resource.id,
            'type': 'custom',
        }]
