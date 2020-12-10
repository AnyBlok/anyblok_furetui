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
from anyblok.tests.test_many2many import _complete_many2many
from anyblok.tests.test_one2many import _complete_one2many
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
    (Time, 'time', {}),
    (Email, 'email', {}),
    (Interval, 'interval', {}),
    (LargeBinary, 'largebinary', {}),
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


@pytest.fixture(scope="class")
def registry_String(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=String)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_Sequence(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=Sequence)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_Password(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=Password)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class", params=[Integer, BigInteger])
def registry_Integer(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=request.param)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class", params=[DateTime, TimeStamp])
def registry_DateTime(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=request.param)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(
    scope="class",
    params=[
        (_minimum_many2one, ['address_id'], '', 0),
        (_complete_many2one, ['id_of_address'], 'persons', 1),
    ])
def registry_many2one(request, bloks_loaded):  # noqa F811
    funct, local_columns, remote_name, required = request.param
    reset_db()
    registry = init_registry_with_bloks(["furetui"], funct)
    request.addfinalizer(registry.close)
    return registry, local_columns, remote_name, required


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
        code = String()
        label = String()

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


class TestResourceFormDefault:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_default):
        registry, _ = registry_default
        transaction = registry.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_default):
        registry, type_ = registry_default
        resource = registry.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": '
                    f'"{type_}", "label": "Col", "tooltip": null, '
                    '"model": null, "required": "0", "readonly": "0", '
                    '"writable": "0", "hidden": "0"}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]


class TestResourceFormString:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_String):
        transaction = registry_String.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_String):
        resource = registry_String.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": '
                    '"string", "label": "Col", "tooltip": null, '
                    '"model": null, "required": "0", "readonly": "0", '
                    '"writable": "0", "hidden": "0", "icon": '
                    '"", "maxlength": 64, "placeholder": ""}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_with_label(self, registry_String):
        resource = registry_String.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" label="Another label"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "string", '
                    '"label": "Another label", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 64, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_with_tooltip(self, registry_String):
        resource = registry_String.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" tooltip="Test"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "string", '
                    '"label": "Col", "tooltip": "Test", "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 64, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_hidden(self, registry_String):
        resource = registry_String.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" hidden/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "string", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "1", "icon": "", "maxlength": 64, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_required(self, registry_String):
        resource = registry_String.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" required/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "string", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "1", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 64, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_readonly(self, registry_String):
        resource = registry_String.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" readonly/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "string", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "1", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 64, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_writable(self, registry_String):
        resource = registry_String.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" writable/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "string", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "1", '
                    '"hidden": "0", "icon": "", "maxlength": 64, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_widget_BarCode(self, registry_String):
        resource = registry_String.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" widget="BarCode"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", '
                    '"type": "barcode", "label": "Col", "tooltip": null, '
                    '"model": null, "required": "0", "readonly": "0", '
                    '"writable": "0", "hidden": "0", "icon": "", '
                    '"options": {}, "placeholder": ""}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_widget_BarCode_and_options(self, registry_String):
        resource = registry_String.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_String) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" widget="BarCode" barcode-foo="bar"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "barcode", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "options": {"foo": "bar"}, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]


class TestResourceFormSequence:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_Sequence):
        transaction = registry_Sequence.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_Sequence):
        resource = registry_Sequence.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Sequence) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "string", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "1", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 64, '
                    '"placeholder": ""}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]


class TestResourceFormPassword:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_Password):
        transaction = registry_Password.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_Password):
        resource = registry_Password.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Password) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "password", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 64, '
                    '"placeholder": "", "reveal": "0"}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_reveal(self, registry_Password):
        resource = registry_Password.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Password) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" reveal/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "password", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "icon": "", "maxlength": 64, '
                    '"placeholder": "", "reveal": "1"}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]


class TestResourceFormSelection:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_Selection):
        transaction = registry_Selection.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_Selection):
        resource = registry_Selection.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Selection) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "selection", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "colors": {}, "selections": '
                    '{"test1": "Test 1", "test2": "Test 2"}}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form',
            }]

    def test_get_definition_and_selections(self, registry_Selection):
        resource = registry_Selection.FuretUI.Resource.Form.insert(
            code='test-list-resource',
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
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "selection", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "colors": {}, "selections": {"test1": '
                    '"T1", "test2": "T2"}}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form',
            }]

    def test_get_definition_and_color(self, registry_Selection):
        resource = registry_Selection.FuretUI.Resource.Form.insert(
            code='test-list-resource',
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
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "selection", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "colors": {"test1": "red", "test2": '
                    '"blue"}, "selections": {"test1": "Test 1", "test2": "Test '
                    '2"}}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form',
            }]

    def test_get_definition_widget_StatusBar(self, registry_Selection):
        resource = registry_Selection.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Selection) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" widget="StatusBar"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", '
                    '"type": "statusbar", "label": "Col", "tooltip": null, '
                    '"model": null, "required": "0", "readonly": "0", '
                    '"writable": "0", "hidden": "0", "dangerous-states": '
                    '[""], "done-states": [""], "selections": {"test1": '
                    '"Test 1", "test2": "Test 2"}}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form',
            }]

    def test_get_definition_widget_StatusBar_and_selections(
        self, registry_Selection
    ):
        resource = registry_Selection.FuretUI.Resource.Form.insert(
            code='test-list-resource',
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
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", '
                    '"type": "statusbar", "label": "Col", "tooltip": null, '
                    '"model": null, "required": "0", "readonly": "0", '
                    '"writable": "0", "hidden": "0", "dangerous-states": [""], '
                    '"done-states": [""], "selections": {"test1": "T1", '
                    '"test2": "T2"}}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form',
            }]

    def test_get_definition_widget_StatusBar_and_done_states(
        self, registry_Selection
    ):
        resource = registry_Selection.FuretUI.Resource.Form.insert(
            code='test-list-resource',
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
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "statusbar", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "dangerous-states": [""], "done-states": '
                    '["test1"], "selections": {"test1": "Test 1", "test2": '
                    '"Test 2"}}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form',
            }]

    def test_get_definition_widget_StatusBar_and_dangerous_states(
        self, registry_Selection
    ):
        resource = registry_Selection.FuretUI.Resource.Form.insert(
            code='test-list-resource',
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
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "statusbar", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "dangerous-states": ["test1"], '
                    '"done-states": [""], "selections": {"test1": "Test 1", '
                    '"test2": "Test 2"}}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form',
            }]


class TestResourceFormInteger:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_Integer):
        transaction = registry_Integer.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_Integer):
        resource = registry_Integer.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_Integer) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "integer", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "max": null, "min": null}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]


class TestResourceFormDateTime:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_DateTime):
        transaction = registry_DateTime.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_DateTime):
        resource = registry_DateTime.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_DateTime) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="col" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "col", "type": "datetime", '
                    '"label": "Col", "tooltip": null, "model": null, '
                    '"required": "0", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "datepicker": {"showWeekNumber": true}, '
                    '"editable": true, "icon": "", "placeholder": "", '
                    '"timepicker": {"enableSeconds": true, "hourFormat": '
                    '"24"}}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['col'],
                'model': 'Model.Test',
                'id': resource.id,
                'type': 'form'
            }]


class TestResourceFormMany2One:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_many2one):
        registry = registry_many2one[0]
        transaction = registry.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_many2one):
        registry, local_columns, remote_name, required = registry_many2one
        resource = registry.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Person', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="address" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "address", "type": "many2one", '
                    '"label": "Address", "tooltip": null, "model": '
                    f'"Model.Address", "required": "{required}", "readonly": '
                    '"0", "writable": "0", "hidden": "0", "display": '
                    '"fields.id", "fields": ["id"], "filter_by": ["id"], '
                    '"limit": 10, '
                    f'"local_columns": ["{", ".join(local_columns)}"], '
                    '"menu": null, '
                    f'"remote_columns": ["id"], "remote_name": "{remote_name}"'
                    ', "resource": null}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['address.id'],
                'id': resource.id,
                'model': 'Model.Person',
                'type': 'form'
            }]

    def test_get_definition_with_display(self, registry_many2one):
        registry, local_columns, remote_name, required = registry_many2one
        resource = registry.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Person', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="address" display="fields.city"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "address", '
                    '"type": "many2one", "label": "Address", "tooltip": null, '
                    f'"model": "Model.Address", "required": "{required}", '
                    '"readonly": "0", "writable": "0", "hidden": "0", '
                    '"display": "fields.city", "fields": ["city"], '
                    '"filter_by": ["id"], "limit": 10, "local_columns": '
                    f'["{", ".join(local_columns)}"], "menu": null, '
                    f'"remote_columns": ["id"], "remote_name": "{remote_name}"'
                    ', "resource": null}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['address.city'],
                'id': resource.id,
                'model': 'Model.Person',
                'type': 'form'
            }]

    def test_get_definition_no_link(self, registry_many2one):
        registry, local_columns, remote_name, required = registry_many2one
        resource = registry.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Person', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="address" no-link/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "address", "type": "many2one", '
                    '"label": "Address", "tooltip": null, "model": '
                    f'"Model.Address", "required": "{required}", "readonly": '
                    '"0", "writable": "0", "hidden": "0", "display": '
                    '"fields.id", "fields": ["id"], "filter_by": ["id"], '
                    '"limit": 10, "local_columns": '
                    f'["{", ".join(local_columns)}"], "menu": null, '
                    '"remote_columns": ["id"], "remote_name": '
                    f'"{remote_name}", "resource": '
                    'null}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['address.id'],
                'id': resource.id,
                'model': 'Model.Person',
                'type': 'form'
            }]

    def test_get_definition_with_menu(self, registry_many2one):
        registry, local_columns, remote_name, required = registry_many2one
        resource = registry.FuretUI.Resource.Form.insert(
            code='test-list-resource',
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
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "address", '
                    '"type": "many2one", "label": "Address", "tooltip": null, '
                    f'"model": "Model.Address", "required": "{required}", '
                    '"readonly": "0", "writable": "0", "hidden": "0", '
                    '"display": "fields.id", "fields": ["id"], "filter_by": '
                    '["id"], "limit": 10, "local_columns": '
                    f'["{", ".join(local_columns)}"], "menu": 1, '
                    '"remote_columns": ["id"], "remote_name": '
                    f'"{remote_name}", '
                    '"resource": 4}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['address.id'],
                'id': resource.id,
                'model': 'Model.Person',
                'type': 'form'
            }]

    def test_get_definition_with_resource(self, registry_many2one):
        registry, local_columns, remote_name, required = registry_many2one
        resource = registry.FuretUI.Resource.Form.insert(
            code='test-list-resource',
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
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": '
                    '"address", "type": "many2one", "label": "Address", '
                    '"tooltip": null, "model": "Model.Address", "required": '
                    f'"{required}", "readonly": "0", "writable": "0", '
                    '"hidden": "0", "display": "fields.id", "fields": ["id"], '
                    '"filter_by": ["id"], "limit": 10, "local_columns": '
                    f'["{", ".join(local_columns)}"], "menu": null, '
                    '"remote_columns": ["id"], "remote_name": '
                    f'"{remote_name}", '
                    '"resource": null}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': ['address.id'],
                'id': resource.id,
                'model': 'Model.Person',
                'type': 'form'
            }]


class TestResourceFormMany2Many:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_many2many):
        transaction = registry_many2many.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_many2many):
        resource = registry_many2many.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Person', template='tmpl_test')

        with TmpTemplate(registry_many2many) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="addresses" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "addresses", "type": '
                    '"many2many", "label": "Addresses", "tooltip": null, '
                    '"model": "Model.Address", "required": "0", "readonly": '
                    '"0", "writable": "0", "hidden": "0", "local_columns": '
                    '["name"], "remote_columns": ["id"], "remote_name": '
                    '"persons"}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Person',
                'type': 'form'
            }]

    def test_get_definition_backref(self, registry_many2many):
        resource = registry_many2many.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Address', template='tmpl_test')

        with TmpTemplate(registry_many2many) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="persons" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "persons", "type": "many2many", '
                    '"label": "Persons", "tooltip": null, "model": '
                    '"Model.Person", "required": "0", "readonly": "0", '
                    '"writable": "0", "hidden": "0", "local_columns": ["id"], '
                    '"remote_columns": ["name"], "remote_name": "addresses"}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Address',
                'type': 'form'
            }]

    def test_get_definition_with_resource(self, registry_many2many):
        resource = registry_many2many.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Person', template='tmpl_test')
        registry_many2many.IO.Mapping.set('resource_call', resource)

        with TmpTemplate(registry_many2many) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field
                        name="addresses"
                        resource-external_id="resource_call"
                        resource-type="form"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "addresses", "type": '
                    '"many2many", "label": "Addresses", "tooltip": null, '
                    '"model": "Model.Address", "required": "0", "readonly": '
                    '"0", "writable": "0", "hidden": "0", "local_columns": '
                    '["name"], "remote_columns": ["id"], "remote_name": '
                    f'"persons", "resource": {resource.id}'
                    '}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Person',
                'type': 'form'
            }]


class TestResourceFormOne2Many:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_one2many):
        transaction = registry_one2many[0].begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition(self, registry_one2many):
        registry, remote_columns = registry_one2many
        resource = registry.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Address', template='tmpl_test')

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field name="persons" />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "persons", "type": "one2many", '
                    '"label": "Persons", "tooltip": null, "model": '
                    '"Model.Person", "required": "0", "readonly": "0", '
                    '"writable": "0", "hidden": "0", "local_columns": ["id"], '
                    f'"remote_columns": ["{", ".join(remote_columns)}"], '
                    '"remote_name": "address"}\' v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Address',
                'type': 'form'
            }]

    def test_get_definition_with_resource(self, registry_one2many):
        registry, remote_columns = registry_one2many
        resource = registry.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Address', template='tmpl_test')
        registry.IO.Mapping.set('resource_call', resource)

        with TmpTemplate(registry) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <field
                        name="persons"
                        resource-external_id="resource_call"
                        resource-type="form"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-field '
                    'v-bind:config=\'{"name": "persons", "type": "one2many", '
                    '"label": "Persons", "tooltip": null, "model": '
                    '"Model.Person", "required": "0", "readonly": "0", '
                    '"writable": "0", "hidden": "0", "local_columns": ["id"], '
                    f'"remote_columns": ["{", ".join(remote_columns)}"], '
                    '"remote_name": "address", "resource": 2}\' '
                    'v-bind:resource="resource" '
                    'v-bind:data="data"></furet-ui-field>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Address',
                'type': 'form'
            }]


class TestResourceFormOther:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_with_buttons):
        transaction = registry_with_buttons.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_definition_div(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <div>Test</div>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><div>Test</div>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_div_with_hidden(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <div hidden>Test</div>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-div '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'hidden\': \'1\', \'props\': '
                    '{}}">Test</furet-ui-div>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_fieldset(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <fieldset>Test</fieldset>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-fieldset '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{}">Test</furet-ui-fieldset>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_fieldset_with_readonly(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <fieldset readonly>Test</fieldset>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-fieldset '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'readonly\': \'1\', \'props\': '
                    '{}}">Test</furet-ui-fieldset>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_fieldset_with_hidden(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <fieldset hidden>Test</fieldset>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-fieldset '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'hidden\': \'1\', \'props\': '
                    '{}}">Test</furet-ui-fieldset>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_fieldset_with_writable(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <fieldset writable>Test</fieldset>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-fieldset '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'writable\': \'1\', \'props\': '
                    '{}}">Test</furet-ui-fieldset>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_tabs(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <tabs name="test">
                        <tab label="Test"
                            Test
                        </tab>
                    </tabs>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-tabs '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'name\': \'test\'}"><furet-ui-tab '
                    'label="Test" v-bind:resource="resource" '
                    'v-bind:data="data" v-bind:config="{}">\n'
                    '                    </furet-ui-tab></furet-ui-tabs>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_tabs_without_name(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <tabs>
                        <tab label="Test"
                            Test
                        </tab>
                    </tabs>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-tabs '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'name\': \'tabs1\'}"><furet-ui-tab '
                    'label="Test" v-bind:resource="resource" '
                    'v-bind:data="data" v-bind:config="{}">\n'
                    '                    </furet-ui-tab></furet-ui-tabs>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_tabs_with_readonly(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <tabs name="test" readonly>
                        <tab label="Test"
                            Test
                        </tab>
                    </tabs>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-tabs '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'readonly\': \'1\', \'props\': '
                    '{\'name\': \'test\'}, \'name\': \'test\'}"><furet-ui-tab '
                    'label="Test" v-bind:resource="resource" '
                    'v-bind:data="data" v-bind:config="{}">\n'
                    '                    </furet-ui-tab></furet-ui-tabs>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_tabs_with_hidden(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <tabs name="test" hidden>
                        <tab label="Test"
                            Test
                        </tab>
                    </tabs>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-tabs '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'hidden\': \'1\', \'props\': {\'name\': '
                    '\'test\'}, \'name\': \'test\'}"><furet-ui-tab '
                    'label="Test" v-bind:resource="resource" '
                    'v-bind:data="data" v-bind:config="{}">\n'
                    '                    </furet-ui-tab></furet-ui-tabs>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_tabs_with_writable(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <tabs name="test" writable>
                        <tab label="Test"
                            Test
                        </tab>
                    </tabs>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-tabs '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'writable\': \'1\', \'props\': '
                    '{\'name\': \'test\'}, \'name\': \'test\'}">'
                    '<furet-ui-tab label="Test" '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{}">\n'
                    '                    </furet-ui-tab></furet-ui-tabs>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_selector_without_any_selection(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <selector name="test"/>
                </template>
            """)
            tmpl.compile()
            with pytest.raises(Exception):
                resource.get_definitions()

    def test_get_definition_selector_with_selection(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <selector selections="{'test': 'Test 1'}"/>
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-selector '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'name\': \'tag0\', '
                    '\'selections\': &quot;{\'test\': \'Test 1\'}&quot;}">'
                    '</furet-ui-selector>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_selector_with_name(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <selector
                        name="myselector"
                        selections="{'test': 'Test 1'}"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-selector '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'name\': \'myselector\', \'selections\': '
                    '&quot;{\'test\': \'Test 1\'}&quot;}"></furet-ui-selector>'
                    '\n                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_selector_with_colors(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <selector
                        selections="{'test': 'Test 1'}"
                        selection_colors="{'test': 'Test 1'}"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-selector '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'name\': \'tag0\', \'selections\': '
                    "&quot;{'test': 'Test 1'}&quot;, 'selection_colors': "
                    '&quot;{\'test\': \'Test 1\'}&quot;}"></furet-ui-selector>'
                    '\n                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_selector_with_model(self, registry_with_buttons):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')
        registry_with_buttons.Test.insert(code='test1', label='Test 1')
        registry_with_buttons.Test.insert(code='test2', label='Test 2')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <selector
                        name="myselector"
                        model="Model.Test"
                        field_code="code"
                        field_label="label"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-selector '
                    'v-bind:resource="resource" v-bind:data="data" '
                    'v-bind:config="{\'name\': \'myselector\', \'selections\': '
                    "{'test1': 'Test 1', 'test2': 'Test "
                    '2\'}}"></furet-ui-selector>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_button_without_any_action(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <button label="test" />
                </template>
            """)
            tmpl.compile()
            with pytest.raises(Exception):
                resource.get_definitions()

    def test_get_definition_button_call_existing_resource(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')
        registry_with_buttons.IO.Mapping.set('resource_call', resource)

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <button
                        label="test"
                        open-resource="resource_call"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-form-button '
                    'v-bind:config=\'{"label": "test", '
                    '"class": [], "open_resource": "resource_call"}\' '
                    'v-bind:resource="resource" v-bind:data="data">'
                    '</furet-ui-form-button>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_button_readonly(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')
        registry_with_buttons.IO.Mapping.set('resource_call', resource)

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <button
                        label="test"
                        readonly
                        open-resource="resource_call"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-form-button '
                    'v-bind:config=\'{"label": "test", "class": [], '
                    '"open_resource": "resource_call", "readonly": "1"}\' '
                    'v-bind:resource="resource" v-bind:data="data">'
                    '</furet-ui-form-button>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_button_hidden(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')
        registry_with_buttons.IO.Mapping.set('resource_call', resource)

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <button
                        label="test"
                        hidden="1"
                        open-resource="resource_call"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-form-button '
                    'v-bind:config=\'{"label": "test", "class": [], '
                    '"open_resource": "resource_call", "hidden": "1"}\' '
                    'v-bind:resource="resource" v-bind:data="data">'
                    '</furet-ui-form-button>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_button_call_unexisting_resource(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <button
                        label="test"
                        open-resource="resource_call"
                    />
                </template>
            """)
            tmpl.compile()
            with pytest.raises(Exception):
                resource.get_definitions()

    def test_get_definition_button_call_undecorated_method(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <button
                        label="test"
                        call="not_decorated"
                    />
                </template>
            """)
            tmpl.compile()
            with pytest.raises(Exception):
                resource.get_definitions()

    def test_get_definition_button_call_decorated_method(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <button
                        label="test"
                        call="simple_method"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions() == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-form-button '
                    'v-bind:config=\'{"label": "test", '
                    '"class": [], "call": "simple_method"}\' '
                    'v-bind:resource="resource" v-bind:data="data">'
                    '</furet-ui-form-button>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_button_call_decorated_method_with_permission(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')
        registry_with_buttons.Pyramid.Authorization.insert(
            model='Model.Test', login='test',
            perms=dict(do_something=dict(matched=True)))

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <button
                        label="test"
                        call="method_with_permission"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions(authenticated_userid='test') == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"><furet-ui-form-button '
                    'v-bind:config=\'{"label": "test", '
                    '"class": [], "call": "method_with_permission"}\' '
                    'v-bind:resource="resource" v-bind:data="data">'
                    '</furet-ui-form-button>\n'
                    '                </div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]

    def test_get_definition_button_call_decorated_method_without_permission(
        self, registry_with_buttons
    ):
        resource = registry_with_buttons.FuretUI.Resource.Form.insert(
            code='test-list-resource',
            model='Model.Test', template='tmpl_test')

        with TmpTemplate(registry_with_buttons) as tmpl:
            tmpl.load_template_from_str("""
                <template id="tmpl_test">
                    <button
                        label="test"
                        call="method_with_permission"
                    />
                </template>
            """)
            tmpl.compile()
            assert resource.get_definitions(authenticated_userid='test') == [{
                'body_template': (
                    '<div xmlns:v-bind="https://vuejs.org/" '
                    'id="tmpl_test"></div>\n'
                    '            '
                ),
                'fields': [],
                'id': resource.id,
                'model': 'Model.Test',
                'type': 'form'
            }]
