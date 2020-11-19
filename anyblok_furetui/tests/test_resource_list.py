import pytest
# from anyblok import Declarations
# from anyblok_furetui import exposed_method
from anyblok.column import (
    Boolean, Json, String, BigInteger, Text, Selection,
    Date, DateTime, Time, Interval, Decimal, Float, LargeBinary, Integer,
    Sequence, Color, Password, UUID, URL, PhoneNumber, Email, Country,
    TimeStamp, Enum)
from anyblok.tests.conftest import init_registry_with_bloks, reset_db
from anyblok.tests.test_column import (
    simple_column, MyTestEnum, has_colour, has_furl, has_phonenumbers,
    has_pycountry)
from ..testing import TmpTemplate


@pytest.fixture(scope="class")
def registry_Selection(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=Selection,
        selections={'test1': 'Test 1', 'test2': 'Test 2'})
    request.addfinalizer(registry.close)
    return registry


PARAMS = [
    (Boolean, 'boolean', {}),
    (Enum, 'enum', {'enum_cls': MyTestEnum}),
    (Json, 'json', {}),
    (Text, 'text', {}),
    (Date, 'date', {}),
    (DateTime, 'datetime', {}),
    (TimeStamp, 'timestamp', {}),
    (Time, 'time', {}),
    (Email, 'email', {}),
    (Interval, 'interval', {}),
    (LargeBinary, 'largebinary', {}),
    (Password, 'password', {}),
    (UUID, 'uuid', {}),
    (Decimal, 'decimal', {}),
    (Float, 'float', {}),
]


if has_colour:
    PARAMS.append((Color, 'color', {}))


if has_furl:
    PARAMS.append((URL, 'url', {}))


if has_phonenumbers:
    PARAMS.append((PhoneNumber, 'phonenumber', {}))


if has_pycountry:
    PARAMS.append((Country, 'country', {}))


@pytest.fixture(scope="class", params=PARAMS)
def registry_default(request, bloks_loaded):  # noqa F811
    reset_db()
    Type, type_, kwargs = request.param
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=Type, **kwargs)
    request.addfinalizer(registry.close)
    return registry, type_


@pytest.fixture(scope="class", params=[String, Sequence])
def registry_String(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=request.param)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class", params=[Integer, BigInteger])
def registry_Integer(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=request.param)
    request.addfinalizer(registry.close)
    return registry


class TestResourceListDefault:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_default):
        registry, _ = registry_default
        transaction = registry.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_default):
        registry, type_ = registry_default
        numeric = True if type_ in ('float', 'decimal') else False
        resource = registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': numeric,
                    'sticky': False,
                    'tooltip': None,
                    'type': type_,
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]


class TestResourceListString:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_String):
        transaction = registry_String.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'string',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_with_label(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" label="Another label"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Another label',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'string',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_with_tooltip(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" tooltip="Test"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': 'Test',
                    'type': 'string',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_sortable(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" sortable/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'string',
                    'sortable': True,
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_column_can_be_hidden(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" column-can-be-hidden/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'column-can-be-hidden': True,
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'string',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_hidden_column(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" hidden-column/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden-column': True,
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'string',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_hidden(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" hidden/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': True,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'string',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_sticky(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" sticky="fields.id==1"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': 'fields.id==1',
                    'tooltip': None,
                    'type': 'string',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_widget_BarCode(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" widget="BarCode"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'barcode',
                    'options': {}
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_widget_BarCode_and_options(self, registry_String):
        resource = registry_String.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" widget="BarCode" barcode-foo="bar"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'barcode',
                    'options': {'foo': 'bar'}
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]


class TestResourceListSelection:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_Selection):
        transaction = registry_Selection.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_Selection):
        resource = registry_Selection.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Selection) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'colors': {},
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'selections': {'test1': 'Test 1', 'test2': 'Test 2'},
                    'sticky': False,
                    'tooltip': None,
                    'type': 'selection',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_and_selections(self, registry_Selection):
        resource = registry_Selection.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Selection) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field
                        name="col"
                        selections="{'test1': 'T1', 'test2': 'T2'}"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'colors': {},
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'selections': {'test1': 'T1', 'test2': 'T2'},
                    'sticky': False,
                    'tooltip': None,
                    'type': 'selection',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_and_color(self, registry_Selection):
        resource = registry_Selection.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Selection) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field
                        name="col"
                        colors="{'test1': 'red', 'test2': 'blue'}"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'colors': {'test1': 'red', 'test2': 'blue'},
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'selections': {'test1': 'Test 1', 'test2': 'Test 2'},
                    'sticky': False,
                    'tooltip': None,
                    'type': 'selection',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_widget_StatusBar(self, registry_Selection):
        resource = registry_Selection.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Selection) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" widget="StatusBar"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'dangerous-states': [''],
                    'done-states': [''],
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'selections': {'test1': 'Test 1', 'test2': 'Test 2'},
                    'sticky': False,
                    'tooltip': None,
                    'type': 'statusbar',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_widget_StatusBar_and_selections(
        self, registry_Selection
    ):
        resource = registry_Selection.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Selection) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field
                        name="col"
                        widget="StatusBar"
                        selections="{'test1': 'T1', 'test2': 'T2'}"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'dangerous-states': [''],
                    'done-states': [''],
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'selections': {'test1': 'T1', 'test2': 'T2'},
                    'sticky': False,
                    'tooltip': None,
                    'type': 'statusbar',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_widget_StatusBar_and_done_states(
        self, registry_Selection
    ):
        resource = registry_Selection.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Selection) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field
                        name="col"
                        widget="StatusBar"
                        done-states="test1"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'dangerous-states': [''],
                    'done-states': ['test1'],
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'selections': {'test1': 'Test 1', 'test2': 'Test 2'},
                    'sticky': False,
                    'tooltip': None,
                    'type': 'statusbar',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_widget_StatusBar_and_dangerous_states(
        self, registry_Selection
    ):
        resource = registry_Selection.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Selection) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field
                        name="col"
                        widget="StatusBar"
                        dangerous-states="test1"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'dangerous-states': ['test1'],
                    'done-states': [''],
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'selections': {'test1': 'Test 1', 'test2': 'Test 2'},
                    'sticky': False,
                    'tooltip': None,
                    'type': 'statusbar',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]


class TestResourceListInteger:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_Integer):
        transaction = registry_Integer.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_Integer):
        resource = registry_Integer.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Integer) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['col', 'id'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'hidden': False,
                    'label': 'Col',
                    'name': 'col',
                    'numeric': False,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'integer',
                }],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]
