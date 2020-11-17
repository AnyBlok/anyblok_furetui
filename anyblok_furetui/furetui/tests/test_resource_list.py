import pytest


@pytest.mark.usefixtures('rollback_registry')
class TestResourceList:

    def test_get_definition_without_template(self, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.System.Model')
        assert resource.get_definitions() == [{
            'buttons': [],
            'fields': ['name', 'is_sql_model', 'name', 'schema', 'table'],
            'filters': [],
            'headers': [
                {
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Is a SQL model',
                    'name': 'is_sql_model',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'boolean'
                },
                {
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Name',
                    'name': 'name',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'string'
                },
                {
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Schema',
                    'name': 'schema',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'string'
                },
                {
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Table',
                    'name': 'table',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'string'
                }
            ],
            'model': 'Model.System.Model',
            'tags': [],
            'title': 'test-list-resource',
            'type': 'list',
            'id': resource.id,
        }]
