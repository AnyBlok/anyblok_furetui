import pytest
from ...testing import TmpTemplate


@pytest.mark.usefixtures('rollback_registry')
class TestResourceForm:

    def test_get_definition_without_template(self, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.System.Model')
        assert resource.get_definitions() == [{
            'body_template': (
                '<div xmlns:v-bind="https://vuejs.org/" class="columns '
                'is-multiline is-mobile"><div class="column is-4-desktop '
                'is-6-tablet is-12-mobile"><furet-ui-field '
                'name="is_sql_model" v-bind:config=\'{"name": '
                '"is_sql_model", "type": "boolean", "label": "Is a SQL '
                'model", "tooltip": null, "model": null, "required": "0", '
                '"readonly": "0", "writable": "0", "hidden": "0"}\' '
                'v-bind:resource="resource" '
                'v-bind:data="data"></furet-ui-field></div><div '
                'class="column is-4-desktop is-6-tablet '
                'is-12-mobile"><furet-ui-field name="name" '
                'v-bind:config=\'{"name": "name", "type": "string", '
                '"label": "Name", "tooltip": null, "model": null, '
                '"required": "1", "readonly": "0", "writable": "0", '
                '"hidden": "0", "icon": "", "maxlength": 256, '
                '"placeholder": ""}\' v-bind:resource="resource" '
                'v-bind:data="data"></furet-ui-field></div><div '
                'class="column is-4-desktop is-6-tablet '
                'is-12-mobile"><furet-ui-field name="schema" '
                'v-bind:config=\'{"name": "schema", "type": "string", '
                '"label": "Schema", "tooltip": null, "model": null, '
                '"required": "0", "readonly": "0", "writable": "0", '
                '"hidden": "0", "icon": "", "maxlength": 64, "placeholder": '
                '""}\' v-bind:resource="resource" '
                'v-bind:data="data"></furet-ui-field></div><div '
                'class="column is-4-desktop is-6-tablet '
                'is-12-mobile"><furet-ui-field name="table" '
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
            'id': resource.id,
        }]

    def test_get_definition_with_template(self, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.System.Model',
            template='tmpl_test')

        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="name" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field name="name" '
                    'v-bind:config=\'{"name": "name", "type": "string", '
                    '"label": "Name", "tooltip": null, "model": null, '
                    '"required": "1", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 256, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['name'],
                'model': 'Model.System.Model',
                'type': 'form',
                'id': resource.id,
            }]

    def test_get_definition_with_template_and_header(self, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.System.Model',
            template='tmpl_test')

        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <header>
                        <h1>{{ fields.name }}</h1>
                    </header>
                    <field name="name" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field name="name" '
                    'v-bind:config=\'{"name": "name", "type": "string", '
                    '"label": "Name", "tooltip": null, "model": null, '
                    '"required": "1", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 256, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'header_template': (
                    '<div xmlns:v-bind="https://vuejs.org/"><h1>{{ '
                    'fields.name }}</h1>\n'
                    '                    </div>\n'
                    '                    '
                ),
                'fields': ['name'],
                'model': 'Model.System.Model',
                'type': 'form',
                'id': resource.id,
            }]

    def test_get_definition_with_template_and_footer(self, rollback_registry):
        resource = rollback_registry.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.System.Model',
            template='tmpl_test')

        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <footer>
                        <h1>{{ fields.name }}</h1>
                    </footer>
                    <field name="name" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field name="name" '
                    'v-bind:config=\'{"name": "name", "type": "string", '
                    '"label": "Name", "tooltip": null, "model": null, '
                    '"required": "1", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 256, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'footer_template': (
                    '<div xmlns:v-bind="https://vuejs.org/"><h1>{{ '
                    'fields.name }}</h1>\n'
                    '                    </div>\n'
                    '                    '
                ),
                'fields': ['name'],
                'model': 'Model.System.Model',
                'type': 'form',
                'id': resource.id,
            }]
