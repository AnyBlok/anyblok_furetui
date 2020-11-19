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
    simple_column, MyTestEnum, has_cryptography, has_passlib, has_colour,
    has_furl, has_phonenumbers, has_pycountry)
from ..testing import TmpTemplate


@pytest.fixture(scope="class")
def registry_Selection(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=Selection,
        selections={'test1': 'Test 1', 'test2': 'Test 2'})
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_Enum(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=Enum,
        enum_cls=MyTestEnum)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_Boolean(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=Boolean)
    request.addfinalizer(registry.close)
    return registry


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


class TestResourceListBoolean:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_Boolean):
        transaction = registry_Boolean.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_Boolean):
        resource = registry_Boolean.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Boolean) as tmpl:
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
                    'type': 'boolean',
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
                    <field name="col" selections="{'test1': 'T1', 'test2': 'T2'}"/>
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
                    <field name="col" colors="{'test1': 'red', 'test2': 'blue'}"/>
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


class TestResourceListEnum:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_Enum):
        transaction = registry_Enum.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_Enum):
        resource = registry_Enum.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Enum) as tmpl:
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
                    'type': 'enum',
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
