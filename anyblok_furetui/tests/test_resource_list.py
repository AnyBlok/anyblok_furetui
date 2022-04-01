import pytest
from datetime import datetime
from anyblok.tests.conftest import init_registry_with_bloks, reset_db
from anyblok import Declarations
from anyblok_furetui import exposed_method
from anyblok.column import (
    Boolean, Json, String, BigInteger, Text, Selection,
    Date, DateTime, Time, Interval, Decimal, Float, LargeBinary, Integer,
    Sequence, Color, Password, UUID, URL, PhoneNumber, Email, Country,
    TimeStamp, Enum)
from anyblok.tests.test_column import (
    simple_column, MyTestEnum, has_colour, has_furl, has_phonenumbers,
    has_pycountry)
from anyblok.relationship import Many2Many
from anyblok.tests.test_many2one import _minimum_many2one, _complete_many2one
from anyblok.tests.test_one2one import _minimum_one2one
from anyblok.tests.test_one2many import _complete_one2many
from anyblok.tests.test_many2many import _complete_many2many
from ..testing import TmpTemplate

register = Declarations.register
Model = Declarations.Model
Mixin = Declarations.Mixin


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


if has_phonenumbers and False:
    PARAMS.append((PhoneNumber, 'phonenumber', {}))


if has_pycountry and False:
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


@pytest.fixture(
    scope="class",
    params=[
        (_minimum_many2one, ['address_id'], ''),
        (_complete_many2one, ['id_of_address'], 'persons'),
    ])
def registry_many2one(request, bloks_loaded):  # noqa F811
    funct, local_columns, remote_name = request.param
    reset_db()
    registry = init_registry_with_bloks(["furetui"], funct)
    request.addfinalizer(registry.close)
    return registry, local_columns, remote_name


@pytest.fixture(scope="class")
def registry_one2one(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(["furetui"], _minimum_one2one)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(
    scope="class",
    params=[
        (_complete_many2one, ['id_of_address']),
        (_complete_one2many, ['address_id']),
    ])
def registry_one2many(request, bloks_loaded):  # noqa F811
    funct, remote_columns = request.param
    reset_db()
    registry = init_registry_with_bloks(["furetui"], funct)
    request.addfinalizer(registry.close)
    return registry, remote_columns


def _complete_many2many_richtext():

    @register(Model)
    class Address:

        id = Integer(primary_key=True)
        street = String()
        zip = String()
        city = String()

    @register(Model)
    class PersonAddress:
        id = Integer(primary_key=True)
        a_id = Integer(
            foreign_key=Model.Address.use('id'), nullable=False)
        p_name = String(
            foreign_key='Model.Person=>name', nullable=False)
        create_at = DateTime(default=datetime.now)
        foo = String(default='bar')

    @register(Model)
    class Person:

        name = String(primary_key=True)
        addresses = Many2Many(model=Model.Address,
                              join_table="personaddress",
                              many2many="persons")


def _minimum_many2many(**kwargs):

    @register(Model)
    class Address:

        id = Integer(primary_key=True)
        street = String()
        zip = String()
        city = String()

    @register(Model)
    class Person:

        name = String(primary_key=True)
        addresses = Many2Many(model=Model.Address, many2many="persons")


@pytest.fixture(
    scope="class",
    params=[
        _complete_many2many,
        _minimum_many2many,
        _complete_many2many_richtext,
    ])
def registry_many2many(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(["furetui"], request.param)
    request.addfinalizer(registry.close)
    return registry


def with_buttons():

    @register(Model)
    class Test:

        id = Integer(primary_key=True)

        @classmethod
        def not_decorated(cls):
            pass

        @exposed_method()
        def simple_method(cls, param=None):
            return param

        @exposed_method(permission='do_something')
        def method_with_permission(cls, param=None):
            return param


@pytest.fixture(scope="class")
def registry_with_buttons(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui", "furetui-auth"], with_buttons)
    registry.Pyramid.User.insert(login='test')

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
                    'numeric': True,
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


class TestResourceListMany2One:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_many2one):
        registry = registry_many2one[0]
        transaction = registry.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_many2one):
        registry, local_columns, remote_name = registry_many2one
        resource = registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Person', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="address" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['address.id', 'name'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'display': 'fields.id',
                    'hidden': False,
                    'label': 'Address',
                    'local_columns': local_columns,
                    'menu': None,
                    'model': 'Model.Address',
                    'name': 'address',
                    'numeric': False,
                    'remote_columns': ['id'],
                    'remote_name': remote_name,
                    'resource': None,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'many2one'
                }],
                'id': resource.id,
                'model': 'Model.Person',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_with_display(self, registry_many2one):
        registry, local_columns, remote_name = registry_many2one
        resource = registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Person', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="address" display="fields.city"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['address.city', 'name'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'display': 'fields.city',
                    'hidden': False,
                    'label': 'Address',
                    'local_columns': local_columns,
                    'menu': None,
                    'model': 'Model.Address',
                    'name': 'address',
                    'numeric': False,
                    'remote_columns': ['id'],
                    'remote_name': remote_name,
                    'resource': None,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'many2one'
                }],
                'id': resource.id,
                'model': 'Model.Person',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_no_link(self, registry_many2one):
        registry, local_columns, remote_name = registry_many2one
        resource = registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Person', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="address" no-link/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['address.id', 'name'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'display': 'fields.id',
                    'hidden': False,
                    'label': 'Address',
                    'local_columns': local_columns,
                    'menu': None,
                    'model': 'Model.Address',
                    'name': 'address',
                    'numeric': False,
                    'remote_columns': ['id'],
                    'remote_name': remote_name,
                    'resource': None,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'many2one'
                }],
                'id': resource.id,
                'model': 'Model.Person',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_with_menu(self, registry_many2one):
        registry, local_columns, remote_name = registry_many2one
        resource = registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Person', template='tmpl_test')
        menu = registry.FuretUI.Menu.Resource.insert(
            label="Resource 1", resource=resource)
        registry.IO.Mapping.set('menu_call', menu)

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="address" menu="menu_call"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['address.id', 'name'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'display': 'fields.id',
                    'hidden': False,
                    'label': 'Address',
                    'local_columns': local_columns,
                    'menu': menu.id,
                    'model': 'Model.Address',
                    'name': 'address',
                    'numeric': False,
                    'remote_columns': ['id'],
                    'remote_name': remote_name,
                    'resource': resource.id,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'many2one'
                }],
                'id': resource.id,
                'model': 'Model.Person',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_with_resource(self, registry_many2one):
        registry, local_columns, remote_name = registry_many2one
        resource = registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Person', template='tmpl_test')
        resource_form = registry.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.Address')
        registry.IO.Mapping.set('resource_call', resource_form)

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="address" resource="resource_call"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['address.id', 'name'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'display': 'fields.id',
                    'hidden': False,
                    'label': 'Address',
                    'local_columns': local_columns,
                    'menu': None,
                    'model': 'Model.Address',
                    'name': 'address',
                    'numeric': False,
                    'remote_columns': ['id'],
                    'remote_name': remote_name,
                    'resource': resource_form.id,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'many2one'
                }],
                'id': resource.id,
                'model': 'Model.Person',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]


class TestResourceListOne2One:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_one2one):
        transaction = registry_one2one.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_one2one):
        resource = registry_one2one.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Person', template='tmpl_test')

        with TmpTemplate(registry_one2one) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="address" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['address.id', 'name'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'display': 'fields.id',
                    'hidden': False,
                    'label': 'Address',
                    'local_columns': ['address_id'],
                    'menu': None,
                    'model': 'Model.Address',
                    'name': 'address',
                    'numeric': False,
                    'remote_columns': ['id'],
                    'remote_name': 'person',
                    'resource': None,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'one2one'
                }],
                'id': resource.id,
                'model': 'Model.Person',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]


class TestResourceListOne2Many:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_one2many):
        transaction = registry_one2many[0].begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_one2many):
        registry, remote_columns = registry_one2many
        resource = registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Address', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="persons" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['id', 'persons.name'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'display': 'fields.name',
                    'hidden': False,
                    'label': 'Persons',
                    'local_columns': ['id'],
                    'menu': None,
                    'model': 'Model.Person',
                    'name': 'persons',
                    'numeric': False,
                    'remote_columns': remote_columns,
                    'remote_name': 'address',
                    'resource': None,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'one2many'
                }],
                'id': resource.id,
                'model': 'Model.Address',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]


class TestResourceListMany2Many:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_many2many):
        transaction = registry_many2many.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_many2many):
        resource = registry_many2many.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Person', template='tmpl_test')

        with TmpTemplate(registry_many2many) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="addresses" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['addresses.id', 'name'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'display': 'fields.id',
                    'hidden': False,
                    'label': 'Addresses',
                    'local_columns': ['name'],
                    'menu': None,
                    'model': 'Model.Address',
                    'name': 'addresses',
                    'numeric': False,
                    'remote_columns': ['id'],
                    'remote_name': 'persons',
                    'resource': None,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'many2many'
                }],
                'id': resource.id,
                'model': 'Model.Person',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_backref(self, registry_many2many):
        resource = registry_many2many.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Address', template='tmpl_test')

        with TmpTemplate(registry_many2many) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="persons" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [],
                'fields': ['id', 'persons.name'],
                'filters': [],
                'headers': [{
                    'component': 'furet-ui-field',
                    'display': 'fields.name',
                    'hidden': False,
                    'label': 'Persons',
                    'local_columns': ['id'],
                    'menu': None,
                    'model': 'Model.Person',
                    'name': 'persons',
                    'numeric': False,
                    'remote_columns': ['name'],
                    'remote_name': 'addresses',
                    'resource': None,
                    'sticky': False,
                    'tooltip': None,
                    'type': 'many2many'
                }],
                'id': resource.id,
                'model': 'Model.Address',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]


class TestResourceListButtons:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_with_buttons, clear_context):
        transaction = registry_with_buttons.begin_nested()
        registry_with_buttons.FuretUI.context.set(userid='test')
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition_without_any_action(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <buttons>
                        <button label="test" />
                    </buttons>
                </template>
            """)
            tmpl.compile()
            with pytest.raises(Exception):
                resource.get_definitions()

    def test_get_definition_call_existing_resource(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')
        registry_with_buttons.IO.Mapping.set('resource_call', resource)

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <buttons>
                        <button
                            label="test"
                            open-resource="resource_call"
                        />
                    </buttons>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [{
                    'label': 'test',
                    'open-resource': 'resource_call',
                    'pks': ['id']
                }],
                'fields': ['id'],
                'filters': [],
                'headers': [],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_call_unexisting_resource(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <buttons>
                        <button
                            label="test"
                            open-resource="resource_call"
                        />
                    </buttons>
                </template>
            """)
            tmpl.compile()
            with pytest.raises(Exception):
                resource.get_definitions()

    def test_get_definition_call_undecorated_method(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <buttons>
                        <button
                            label="test"
                            call="not_decorated"
                        />
                    </buttons>
                </template>
            """)
            tmpl.compile()
            with pytest.raises(Exception):
                resource.get_definitions()

    def test_get_definition_call_decorated_method(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <buttons>
                        <button
                            label="test"
                            call="simple_method"
                        />
                    </buttons>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'buttons': [{
                    'call': 'simple_method',
                    'label': 'test',
                    'pks': ['id']
                }],
                'fields': ['id'],
                'filters': [],
                'headers': [],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_call_decorated_method_with_permission(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')
        registry_with_buttons.Pyramid.Authorization.insert(
            model='Model.Test', login='test',
            perms=dict(do_something=dict(matched=True)))

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <buttons>
                        <button
                            label="test"
                            call="method_with_permission"
                        />
                    </buttons>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions(authenticated_userid='test') == [{
                'buttons': [{
                    'call': 'method_with_permission',
                    'label': 'test',
                    'pks': ['id']
                }],
                'fields': ['id'],
                'filters': [],
                'headers': [],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]

    def test_get_definition_call_decorated_method_without_permission(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <buttons>
                        <button
                            label="test"
                            call="method_with_permission"
                        />
                    </buttons>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions(authenticated_userid='test') == [{
                'buttons': [],
                'fields': ['id'],
                'filters': [],
                'headers': [],
                'id': resource.id,
                'model': 'Model.Test',
                'tags': [],
                'title': 'test-list-resource',
                'type': 'list'
            }]
