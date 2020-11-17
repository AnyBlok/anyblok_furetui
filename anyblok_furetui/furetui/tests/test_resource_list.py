import pytest
from ...testing import TmpTemplate


@pytest.mark.usefixtures('rollback_registry')
class TestResourceList:

    def test_get_definition_without_template(self, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.System.Model')
        assert resource.get_definitions() == [{
            'buttons': [],
            'fields': ['is_sql_model', 'name', 'schema', 'table'],
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

    def test_get_definition_with_template(self, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.System.Model', template='tmpl_test')

        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="name" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['name'],
                'filters': [],
                'headers': [
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
                ],
                'model': 'Model.System.Model',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list',
                'id': resource.id,
            }]

    def test_get_definition_with_template_and_filters_1(
        self, rollback_registry
    ):
        resource = rollback_registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.System.Model', template='tmpl_test')
        rollback_registry.FuretUI.Resource.Filter.insert(
            key='name', list=resource, label="Test name",
            values="anyblok-core,furetui")

        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="name" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['name'],
                'filters': [{
                    'key': 'name',
                    'label': 'Test name',
                    'mode': 'include',
                    'op': 'or-ilike',
                    'values': ['anyblok-core', 'furetui']
                }],
                'headers': [
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
                ],
                'model': 'Model.System.Model',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list',
                'id': resource.id,
            }]

    def test_get_definition_with_template_and_filters_2(
        self, rollback_registry
    ):
        resource = rollback_registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.System.Model', template='tmpl_test')
        rollback_registry.FuretUI.Resource.Filter.insert(
            key='name', list=resource, label="Test name")

        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="name" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['name'],
                'filters': [{
                    'key': 'name',
                    'label': 'Test name',
                    'mode': 'include',
                    'op': 'or-ilike',
                    'values': []
                }],
                'headers': [
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
                ],
                'model': 'Model.System.Model',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list',
                'id': resource.id,
            }]

    def test_get_definition_with_template_and_tags(
        self, rollback_registry
    ):
        resource = rollback_registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.System.Model', template='tmpl_test')
        rollback_registry.FuretUI.Resource.Tags.insert(
            key='from_furetui', list=resource, label="From FuretUI")

        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="name" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['name'],
                'filters': [],
                'headers': [
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
                ],
                'model': 'Model.System.Model',
                'tags': [{
                    'key': 'from_furetui',
                    'label': 'From FuretUI',
                }],
                'title': 'test-list-resource',
                'type': 'list',
                'id': resource.id,
            }]
