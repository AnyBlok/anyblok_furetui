import datetime
import pytest
import pytz
import time
import enum
from uuid import uuid1
from os import urandom
from decimal import Decimal as D
from anyblok import Declarations
from anyblok.testing import sgdb_in
from anyblok.column import (
    Boolean, String, BigInteger, Text, Selection, Date, DateTime, Time,
    Interval, Decimal, Float, LargeBinary, Integer, Sequence, Color, UUID,
    URL, PhoneNumber, Email, Country, TimeStamp)
from anyblok.relationship import Many2One, One2One, One2Many, Many2Many
from anyblok.field import FieldException, Function
from anyblok_furetui.field import Contextual
from anyblok_furetui.factory import ContextualModelFactory
from anyblok.tests.conftest import init_registry_with_bloks, reset_db


# TODO find a better way to declare identity model
# TODO find a good solution to select a fallback identity instance (lang)


register = Declarations.register
Model = Declarations.Model


def funct_contextual_model(ColumnType=None, **kwargs):

    class ProjectMixin:

        @classmethod
        def get_others(cls):
            return {
                'foo': 'bar',
                'bar': 'foo',
            }

        @classmethod
        def get_other(cls):
            return 'foo'

    @Declarations.register(Declarations.Model)
    class Project:

        id = Integer(primary_key=True)

    @register(Model, factory=ContextualModelFactory)
    class Test:

        @classmethod
        def define_contextual_models(cls):
            res = super().define_contextual_models()
            res.update({
                'project': {
                    'model': cls.anyblok.Project,
                    'mixins': [
                        ProjectMixin,
                    ]
                },
            })
            return res

        id = Integer(primary_key=True)
        other = Contextual(field=ColumnType(**kwargs), identity='project')


def dt(day):
    return datetime.datetime(2022, 1, day, 12, 13, 14).replace(
        tzinfo=pytz.timezone(time.tzname[0]))


class MyTestEnum(enum.Enum):
    foo = 'foo'
    bar = 'bar'
    foobar = 'foobar'


COLUMNS = [
    (String, 'foo', 'bar', 'foo-bar', {}),
    (Selection, 'foo', 'bar', 'foo-bar',
     {'selections': {x: x for x in ('foo', 'bar', 'foo-bar')}}),
    (Text, 'foo', 'bar', 'foo-bar', {}),
    (Integer, 1, 2, 3, {}),
    (BigInteger, 1, 2, 3, {}),
    (Float, 1., 2., 3., {}),
    (Decimal, D('1.'), D('2.'), D('3.'), {}),
    (Interval,  datetime.timedelta(days=1), datetime.timedelta(days=2),
     datetime.timedelta(days=3), {}),
    (Email, 'foo@ab.org', 'bar@ab.org', 'foo-bar@ab.org', {}),
    (Date, datetime.date(2022, 1, 1), datetime.date(2022, 1, 2),
     datetime.date(2022, 1, 3), {}),
    (DateTime, dt(1), dt(2), dt(3), {}),
    (Time, datetime.time(1, 1, 1), datetime.time(1, 1, 2),
     datetime.time(1, 1, 3), {}),
    (LargeBinary, urandom(10), urandom(20), urandom(30), {}),
    (Boolean, True, False, True, {}),
]


if not sgdb_in(['MySQL', 'MariaDB']):
    COLUMNS.append((UUID, uuid1(), uuid1(), uuid1(), {}))

if not sgdb_in(['MsSQL']):
    COLUMNS.append((TimeStamp, dt(1), dt(2), dt(3), {}))


try:
    import colour
    COLUMNS.append((Color, colour.Color('red'), colour.Color('green'),
                    colour.Color('blue'), {}))
except Exception:
    pass

try:
    import furl  # noqa
    COLUMNS.append((URL,
                    furl.furl('http://doc.anyblok.org'),
                    furl.furl('http://doc.furetui.org'),
                    furl.furl('http://doc.anyblok-furetui.org'),
                    {}))
except Exception:
    pass


try:
    import phonenumbers  # noqa
    from sqlalchemy_utils import PhoneNumber as PN
    COLUMNS.append((PhoneNumber,
                    PN("+120012301", None),
                    PN("+120012302", None),
                    PN("+120012303", None),
                    {}))
except Exception:
    pass

try:
    import pycountry  # noqa
    COLUMNS.append((Country,
                    pycountry.countries.get(alpha_2='FR'),
                    pycountry.countries.get(alpha_2='JN'),
                    pycountry.countries.get(alpha_2='DE'),
                    {}))
except Exception:
    pass


@pytest.fixture(scope="class", params=COLUMNS)
def column_definition(request, bloks_loaded):
    return request.param


@pytest.fixture(scope="class")
def registry_contextual_model(request, bloks_loaded, column_definition):  # noqa F811
    reset_db()
    column, value1, value2, value3, kwargs = column_definition
    registry = init_registry_with_bloks(
        ["furetui"], funct_contextual_model,
        ColumnType=column, **kwargs
    )
    request.addfinalizer(registry.close)
    return registry


class TestContextualModel:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_contextual_model, column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        transaction = registry.begin_nested()

        self.project1 = registry.Project.insert()
        self.project2 = registry.Project.insert()
        self.project3 = registry.Project.insert()
        self.test = registry.Test.insert()
        registry.Test.Project.insert(
            relate=self.test, project=self.project1, other=value1)
        registry.Test.Project.insert(
            relate=self.test, project=self.project2, other=value2)

        request.addfinalizer(transaction.rollback)
        return

    def test_insert(self, registry_contextual_model, column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project3):
            test = registry.Test.insert(other=value3)
            assert test.other == value3

    def test_insert_without_context(self, registry_contextual_model,
                                    column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        with pytest.raises(FieldException):
            registry.Test.insert(other=value3)

    def test_get(self, registry_contextual_model, column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project1):
            assert self.test.other == value1

    def test_get_without_context(self, registry_contextual_model):
        with pytest.raises(FieldException):
            self.test.other

    def test_set_existing_value(self, registry_contextual_model,
                                column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project2):
            assert self.test.other == value2
            self.test.other = value3
            assert self.test.other == value3

    def test_set_new_value(self, registry_contextual_model, column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project3):
            assert not self.test.other
            self.test.other = value3
            assert self.test.other == value3

    def test_set_without_context(self, registry_contextual_model):
        with pytest.raises(FieldException):
            self.test.other = 'bar2'

    def test_del(self, registry_contextual_model, column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project1):
            assert self.test.other == value1
            del self.test.other
            assert not self.test.other

    def test_delete_entry_from_query_1(self, registry_contextual_model,
                                       column_definition):
        registry = registry_contextual_model
        assert registry.Test.Project.query().filter_by(
            relate=self.test).count() == 2
        registry.Test.query().filter_by(id=self.test.id).delete()
        assert registry.Test.Project.query().filter_by(
            relate=self.test).count() == 0

    def test_delete_entry_from_query_2(self, registry_contextual_model,
                                       column_definition):
        registry = registry_contextual_model
        assert registry.Test.Project.query().filter_by(
            relate=self.test).count() == 2
        Test = registry.Test
        Test.execute_sql_statement(
            Test.delete_sql_statement().where(Test.id == self.test.id))
        assert registry.Test.Project.query().filter_by(
            relate=self.test).count() == 0

    def test_delete_entry_from_method(self, registry_contextual_model,
                                      column_definition):
        registry = registry_contextual_model
        assert registry.Test.Project.query().filter_by(
            relate=self.test).count() == 2
        self.test.delete()
        assert registry.Test.Project.query().filter_by(
            relate=self.test).count() == 0

    def test_del_without_context(self, registry_contextual_model):
        with pytest.raises(FieldException):
            del self.test.other

    def test_expr(self, registry_contextual_model, column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter_by(
                other=value1).one()

    def test_expr_with_another_context(self, registry_contextual_model,
                                       column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project2):
            assert registry.Test.query().filter_by(
                other=value1).one_or_none() is None

    def test_expr_without_context(self, registry_contextual_model,
                                  column_definition):
        registry = registry_contextual_model
        column, value1, value2, value3, kwargs = column_definition
        with pytest.raises(FieldException):
            registry.Test.query().filter_by(other=value1).one_or_none()

    def test_field_description(self, registry_contextual_model,
                               column_definition):
        registry = registry_contextual_model
        fd = registry.Test.fields_description("other")
        fd2 = registry.Test.Project.fields_description("other").copy()
        fd2['other'].update({'identity': 'project',
                             'identity_model': 'Model.Test.Project'})
        assert fd == fd2


DEFAULT = [
    [String, {'default': 'foo'}],
    [Selection, {'selections': 'get_others', 'default': 'foo'}],
    [Selection, {'selections': 'get_others', 'default': 'get_other'}],
]


@pytest.fixture(scope="class", params=DEFAULT)
def registry_contextual_default_model(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], funct_contextual_model,
        ColumnType=request.param[0], **request.param[1])
    request.addfinalizer(registry.close)
    return registry


class TestContextualDefaultModel:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_contextual_default_model):
        registry = registry_contextual_default_model
        transaction = registry.begin_nested()

        self.project1 = registry.Project.insert()

        request.addfinalizer(transaction.rollback)
        return

    def test_default(self, registry_contextual_default_model):
        registry = registry_contextual_default_model
        assert registry.Test.get_default_values().get('other') == 'foo'

    def test_default2(self, registry_contextual_default_model):
        registry = registry_contextual_default_model
        assert registry.Test.Project.get_default_values().get('other') == 'foo'

    def test_default3(self, registry_contextual_default_model):
        registry = registry_contextual_default_model
        with registry.Project.context.set(project=self.project1):
            test = registry.Test.insert()
            assert test.other == 'foo'


def funct_contextual_model_multi_pk():

    @Declarations.register(Declarations.Model)
    class Project:

        id = Integer(primary_key=True)
        code = String(primary_key=True)

    @register(Model, factory=ContextualModelFactory)
    class Test:

        @classmethod
        def define_contextual_models(cls):
            res = super().define_contextual_models()
            res.update({
                'project': {
                    'model': cls.anyblok.Project,
                },
            })
            return res

        id = Integer(primary_key=True)
        code = String(primary_key=True)
        other = Contextual(field=String(), identity='project')


@pytest.fixture(scope="class")
def registry_contextual_model_multi_pk(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], funct_contextual_model_multi_pk)
    request.addfinalizer(registry.close)
    return registry


class TestContextualModelMultiPk:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        transaction = registry.begin_nested()

        self.project1 = registry.Project.insert(code='test')
        self.project2 = registry.Project.insert(code='test')
        self.project3 = registry.Project.insert(code='test')
        self.test = registry.Test.insert(code='test')
        registry.Test.Project.insert(
            relate=self.test, project=self.project1, other='foo')
        registry.Test.Project.insert(
            relate=self.test, project=self.project2, other='bar')

        request.addfinalizer(transaction.rollback)
        return

    def test_insert(self, registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        with registry.Project.context.set(project=self.project3):
            test = registry.Test.insert(code='test', other='foo-bar')
            assert test.other == 'foo-bar'

    def test_insert_without_context(self, registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        with pytest.raises(FieldException):
            registry.Test.insert(code='test', other='foo-bar')

    def test_get(self, registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        with registry.Project.context.set(project=self.project1):
            assert self.test.other == 'foo'

    def test_get_without_context(self, registry_contextual_model_multi_pk):
        with pytest.raises(FieldException):
            self.test.other

    def test_set_existing_value(self, registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        with registry.Project.context.set(project=self.project2):
            assert self.test.other == 'bar'
            self.test.other = 'foo-bar'
            assert self.test.other == 'foo-bar'

    def test_set_new_value(self, registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        with registry.Project.context.set(project=self.project3):
            assert not self.test.other
            self.test.other = 'foo-bar'
            assert self.test.other == 'foo-bar'

    def test_set_without_context(self, registry_contextual_model_multi_pk):
        with pytest.raises(FieldException):
            self.test.other = 'bar2'

    def test_del(self, registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        with registry.Project.context.set(project=self.project1):
            assert self.test.other == 'foo'
            del self.test.other
            assert not self.test.other

    def test_del_without_context(self, registry_contextual_model_multi_pk):
        with pytest.raises(FieldException):
            del self.test.other

    def test_expr(self, registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter_by(
                other='foo').one()

    def test_expr_with_another_context(self,
                                       registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        with registry.Project.context.set(project=self.project2):
            assert registry.Test.query().filter_by(
                other='foo').one_or_none() is None

    def test_expr_without_context(self, registry_contextual_model_multi_pk):
        registry = registry_contextual_model_multi_pk
        with pytest.raises(FieldException):
            registry.Test.query().filter_by(other='foo').one_or_none()


def funct_contextual_model_multi_fields():

    @Declarations.register(Declarations.Model)
    class Project:

        id = Integer(primary_key=True)

    @Declarations.register(Declarations.Model)
    class Lang:

        id = Integer(primary_key=True)

    @register(Model, factory=ContextualModelFactory)
    class Test:

        @classmethod
        def define_contextual_models(cls):
            res = super().define_contextual_models()
            res.update({
                'project': {
                    'model': cls.anyblok.Project,
                },
                'lang': {
                    'model': cls.anyblok.Lang,
                },
            })
            return res

        id = Integer(primary_key=True)
        other = Contextual(field=String(nullable=False), identity='project')
        label = Contextual(field=String(nullable=False), identity='lang')
        description = Contextual(field=String(nullable=False), identity='lang')


@pytest.fixture(scope="class")
def registry_contextual_model_multi_fields(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], funct_contextual_model_multi_fields)
    request.addfinalizer(registry.close)
    return registry


class TestContextualModelMultiFields:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_contextual_model_multi_fields):
        registry = registry_contextual_model_multi_fields
        transaction = registry.begin_nested()

        self.project1 = registry.Project.insert()
        self.project2 = registry.Project.insert()
        self.project3 = registry.Project.insert()

        self.lang1 = registry.Lang.insert()
        self.lang2 = registry.Lang.insert()

        self.test = registry.Test.insert()

        registry.Test.Project.insert(
            relate=self.test, project=self.project1, other='foo')
        registry.Test.Project.insert(
            relate=self.test, project=self.project2, other='bar')

        registry.Test.Lang.insert(
            relate=self.test, lang=self.lang1, label='label1',
            description='description1')

        request.addfinalizer(transaction.rollback)
        return

    def test_insert(self, registry_contextual_model_multi_fields):
        registry = registry_contextual_model_multi_fields
        with registry.Project.context.set(project=self.project3,
                                          lang=self.lang2):
            test = registry.Test.insert(
                other='foo-bar', label="label2", description="description2")
            assert test.label == 'label2'
            assert test.description == 'description2'

    def test_insert_without_context(self,
                                    registry_contextual_model_multi_fields):
        registry = registry_contextual_model_multi_fields
        with pytest.raises(FieldException):
            registry.Test.insert(other='foo-bar', label="label2",
                                 description="description2")

    def test_get(self, registry_contextual_model_multi_fields):
        registry = registry_contextual_model_multi_fields
        with registry.Project.context.set(project=self.project1,
                                          lang=self.lang1):
            assert self.test.other == 'foo'
            assert self.test.label == 'label1'
            assert self.test.description == 'description1'

    def test_set_existing_value(self, registry_contextual_model_multi_fields):
        registry = registry_contextual_model_multi_fields
        with registry.Project.context.set(project=self.project1,
                                          lang=self.lang1):
            assert self.test.label == 'label1'
            self.test.label = 'label3'
            assert self.test.label == 'label3'

    def test_set_new_value(self, registry_contextual_model_multi_fields):
        registry = registry_contextual_model_multi_fields
        with registry.Project.context.set(project=self.project3,
                                          lang=self.lang2):
            self.test.label = 'label2'

    def test_del(self, registry_contextual_model_multi_fields):
        registry = registry_contextual_model_multi_fields
        with registry.Project.context.set(project=self.project1):
            del self.test.other

    def test_expr(self, registry_contextual_model_multi_fields):
        registry = registry_contextual_model_multi_fields
        with registry.Project.context.set(project=self.project1,
                                          lang=self.lang1):
            assert self.test is registry.Test.query().filter_by(
                other='foo', label='label1').one()


def funct_contextual_model_many2one(multipk=False):

    @Declarations.register(Declarations.Model)
    class Project:

        id = Integer(primary_key=True)

    @Declarations.register(Declarations.Model)
    class Other:

        id = Integer(primary_key=True)
        code = String(primary_key=multipk)

    @register(Model, factory=ContextualModelFactory)
    class Test:

        @classmethod
        def define_contextual_models(cls):
            res = super().define_contextual_models()
            res.update({
                'project': {
                    'model': cls.anyblok.Project,
                },
            })
            return res

        id = Integer(primary_key=True)
        other = Contextual(field=Many2One(model=Model.Other),
                           identity='project')


@pytest.fixture(scope="class", params=[True, False])
def registry_contextual_model_many2one(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], funct_contextual_model_many2one,
        multipk=request.param)
    request.addfinalizer(registry.close)
    return registry


class TestContextualModelMany2One:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        transaction = registry.begin_nested()

        self.project1 = registry.Project.insert()
        self.project2 = registry.Project.insert()
        self.project3 = registry.Project.insert()

        self.other1 = registry.Other.insert(code='test')
        self.other2 = registry.Other.insert(code='test')

        self.test = registry.Test.insert()

        registry.Test.Project.insert(
            relate=self.test, project=self.project1, other=self.other1)
        registry.Test.Project.insert(
            relate=self.test, project=self.project2, other=self.other2)

        request.addfinalizer(transaction.rollback)
        return

    def test_insert(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project3):
            test = registry.Test.insert(other=self.other2)
            assert test.other == self.other2

    def test_insert_without_context(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with pytest.raises(FieldException):
            registry.Test.insert(other=self.other2)

    def test_get(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test.other == self.other1

    def test_get_without_context(self, registry_contextual_model_many2one):
        with pytest.raises(FieldException):
            self.test.other

    def test_set_existing_value(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project2):
            assert self.test.other == self.other2
            self.test.other = self.other1
            assert self.test.other == self.other1

    def test_set_new_value(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project3):
            assert not self.test.other
            self.test.other = self.other2
            assert self.test.other == self.other2

    def test_set_without_context(self, registry_contextual_model_many2one):
        with pytest.raises(FieldException):
            self.test.other = self.other2

    def test_del(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test.other == self.other1
            del self.test.other
            assert not self.test.other

    def test_del_without_context(self, registry_contextual_model_many2one):
        with pytest.raises(FieldException):
            del self.test.other

    def test_expr(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter(
                registry.Test.other == self.other1).one()

    def test_expr_2(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter_by(
                other=self.other1).one()

    def test_expr_3(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter(
                registry.Test.other.is_(self.other1)).one()

    def test_expr_4(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter(
                registry.Test.other.isnot(self.other2)).one()

    def test_expr_5(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert registry.Test.query().filter(
                registry.Test.other.isnot(self.other1)).one_or_none(
                ) is None

    def test_expr_6(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert registry.Test.query().filter(
                registry.Test.other != self.other1).one_or_none() is None

    def test_expr_7(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter(
                registry.Test.other != self.other2).one_or_none()

    def test_expr_8(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter(
                registry.Test.other.in_([self.other1])).one()

    def test_expr_9(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter(
                registry.Test.other.in_([self.other1, self.other2])).one()

    def test_expr_10(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert registry.Test.query().filter(
                registry.Test.other.in_([self.other2])).one_or_none(
                ) is None

    def test_expr_11(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert registry.Test.query().filter(
                registry.Test.other.notin([self.other1])).one_or_none(
                ) is None

    def test_expr_12(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter(
                registry.Test.other.notin([self.other2])).one()

    def test_expr_with_another_context(self,
                                       registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with registry.Project.context.set(project=self.project2):
            assert registry.Test.query().filter(
                registry.Test.other == self.other1).one_or_none() is None

    def test_expr_without_context(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        with pytest.raises(FieldException):
            registry.Test.query().filter_by(other=self.other1).one_or_none()

    def test_field_description(self, registry_contextual_model_many2one):
        registry = registry_contextual_model_many2one
        fd = registry.Test.fields_description("other")
        fd2 = registry.Test.Project.fields_description("other").copy()
        fd2['other'].update({'identity': 'project',
                             'identity_model': 'Model.Test.Project'})
        assert fd == fd2


def funct_contextual_model_fallback():

    @Declarations.register(Declarations.Model)
    class Lang:

        code = String(primary_key=True)

    @register(Model, factory=ContextualModelFactory)
    class Test:

        @classmethod
        def define_contextual_models(cls):
            res = super().define_contextual_models()
            res.update({
                'lang': {
                    'model': cls.anyblok.Lang,
                    'fallback': 'en',
                    'fallback_adapter': lambda x: (
                        cls.anyblok.Lang.query().filter_by(code=x).one())
                },
            })
            return res

        id = Integer(primary_key=True)
        label = Contextual(field=String(nullable=False), identity='lang')


@pytest.fixture(scope="class")
def registry_contextual_model_fallback(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], funct_contextual_model_fallback)
    request.addfinalizer(registry.close)
    return registry


class TestContextualModelFallback:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_contextual_model_fallback):
        registry = registry_contextual_model_fallback
        transaction = registry.begin_nested()

        self.lang1 = registry.Lang.insert(code='fr')
        self.lang2 = registry.Lang.insert(code='en')
        self.lang3 = registry.Lang.insert(code='de')

        self.test = registry.Test.insert()

        request.addfinalizer(transaction.rollback)
        return

    def test_insert_on_fallback(self, registry_contextual_model_fallback):
        registry = registry_contextual_model_fallback
        with registry.Lang.context.set(lang=self.lang2):
            test = registry.Test.insert(label="label2")
            assert test.label == 'label2'

        with registry.Lang.context.set(lang=self.lang1):
            assert test.label == 'label2'

        with registry.Lang.context.set(lang=self.lang3):
            assert test.label == 'label2'

    def test_insert_without_fallback_filled(
        self, registry_contextual_model_fallback
    ):
        registry = registry_contextual_model_fallback
        with registry.Lang.context.set(lang=self.lang1):
            test = registry.Test.insert(label="label1")
            assert test.label == 'label1'

        with registry.Lang.context.set(lang=self.lang2):
            assert test.label == 'label1'

        with registry.Lang.context.set(lang=self.lang3):
            assert test.label == 'label1'

    def test_set_on_fallback(self, registry_contextual_model_fallback):
        registry = registry_contextual_model_fallback
        with registry.Lang.context.set(lang=self.lang1):
            test = registry.Test.insert(label="label1")
            assert test.label == 'label1'

        with registry.Lang.context.set(lang=self.lang2):
            test.label = 'label2'

        with registry.Lang.context.set(lang=self.lang3):
            assert test.label == 'label2'

        with registry.Lang.context.set(lang=self.lang1):
            assert test.label == 'label1'

    def test_set_on_another_that_fallback(self,
                                          registry_contextual_model_fallback):
        registry = registry_contextual_model_fallback
        with registry.Lang.context.set(lang=self.lang2):
            test = registry.Test.insert(label="label2")
            assert test.label == 'label2'

        with registry.Lang.context.set(lang=self.lang1):
            test.label == 'label1'

        with registry.Lang.context.set(lang=self.lang3):
            assert test.label == 'label2'

        with registry.Lang.context.set(lang=self.lang2):
            assert test.label == 'label2'

    def test_del_on_fallback(self, registry_contextual_model_fallback):
        registry = registry_contextual_model_fallback
        with registry.Lang.context.set(lang=self.lang2):
            test = registry.Test.insert(label="label2")
            with pytest.raises(FieldException):
                del test.label

    def test_expr_on_fallback(self, registry_contextual_model_fallback):
        registry = registry_contextual_model_fallback
        with registry.Lang.context.set(lang=self.lang2):
            test = registry.Test.insert(label="label2")
            assert test is registry.Test.query().filter_by(
                label='label2').one()

    def test_expr_on_another_than_fallback(
        self, registry_contextual_model_fallback
    ):
        registry = registry_contextual_model_fallback
        with registry.Lang.context.set(lang=self.lang2):
            test = registry.Test.insert(label="label2")

        with registry.Lang.context.set(lang=self.lang1):
            assert test is registry.Test.query().filter_by(
                label='label2').one()


class TestDefinition:

    def test_autodoc(self, column_definition):
        column, value1, value2, value3, kwargs = column_definition
        field = column(**kwargs)
        col = Contextual(field=field, identity='foo')
        assert col.autodoc()

    def test_forbid_without_field(self):
        with pytest.raises(FieldException):
            Contextual(identity='foo')

    def test_forbid_without_identity(self):
        with pytest.raises(FieldException):
            Contextual(field=String())

    def test_forbid_function_field(self):
        with pytest.raises(FieldException):
            Contextual(field=Function(fget='foo'), identity='foo')

    def test_forbid_function_sequence(self):
        with pytest.raises(FieldException):
            Contextual(field=Sequence(), identity='foo')

    def test_forbid_many2one_with_many2one_backref(self):
        with pytest.raises(FieldException):
            Contextual(field=Many2One(model='Model.System.Blok',
                                      one2many='foo'),
                       identity='foo')

    def test_forbid_many2one_with_one2one(self):
        with pytest.raises(FieldException):
            Contextual(field=One2One(model='Model.System.Blok'), identity='foo')

    def test_forbid_many2one_with_many2many(self):
        with pytest.raises(FieldException):
            Contextual(field=Many2Many(model='Model.System.Blok'),
                       identity='foo')

    def test_forbid_many2one_with_one2many(self):
        with pytest.raises(FieldException):
            Contextual(field=One2Many(model='Model.System.Blok'),
                       identity='foo')
