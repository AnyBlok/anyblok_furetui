import pytest


@pytest.mark.usefixtures('rollback_registry')
class TestResourceSet:

    def test_get_definition_without_template(self, rollback_registry):
        resource_list = rollback_registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.System.Model')
        resource_form = rollback_registry.FuretUI.Resource.Form.insert(
            code='test-form-resource', model='Model.System.Model')
        resource = rollback_registry.FuretUI.Resource.Set.insert(
            code='test-set-resource', form=resource_form, list=resource_list)

        acl = True
        auth = rollback_registry.System.Blok.query().get('auth')
        if auth.state == 'installed':
            acl = False

        assert resource.get_definitions() == [
            {
                'type': 'set',
                'id': resource.id,
                'can_create': acl,
                'can_delete': acl,
                'can_read': acl,
                'can_update': acl,
                'form': resource_form.id,
                'forms': [],
                'multi': resource_list.id,
                'pks': ['name'],
            },
            {
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" class="columns '
                    'is-multiline is-mobile"><div class="column is-4-desktop '
                    'is-6-tablet is-12-mobile"><furet-ui-field '
                    'v-bind:config=\'{"name": '
                    '"is_sql_model", "type": "boolean", "label": "Is a SQL '
                    'model", "tooltip": null, "model": null, "required": "0", '
                    '"readonly": "0", "writable": "0", "hidden": "0"}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field></div><div '
                    'class="column is-4-desktop is-6-tablet '
                    'is-12-mobile"><furet-ui-field '
                    'v-bind:config=\'{"name": "name", "type": "string", '
                    '"label": "Name", "tooltip": null, "model": null, '
                    '"required": "1", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 256, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field></div><div '
                    'class="column is-4-desktop is-6-tablet '
                    'is-12-mobile"><furet-ui-field '
                    'v-bind:config=\'{"name": "schema", "type": "string", '
                    '"label": "Schema", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 64, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field></div><div '
                    'class="column is-4-desktop is-6-tablet '
                    'is-12-mobile"><furet-ui-field '
                    'v-bind:config=\'{"name": "table", "type": "string", '
                    '"label": "Table", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 256, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field></div></div>'
                ),
                'fields': ['is_sql_model', 'name', 'schema', 'table'],
                'model': 'Model.System.Model',
                'type': 'form',
                'id': resource_form.id,
            },
            {
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
                'id': resource_list.id,
            },
        ]
