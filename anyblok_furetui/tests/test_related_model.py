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
    Boolean, Json, String, BigInteger, Text, Selection,
    Date, DateTime, Time, Interval, Decimal, Float, LargeBinary, Integer,
    Sequence, Color, Password, UUID, URL, PhoneNumber, Email, Country,
    TimeStamp, Enum)
from anyblok.relationship import Many2One, One2One, One2Many, Many2Many
from anyblok.field import FieldException
from anyblok_furetui.field import Related
from anyblok_furetui.factory import RelatedModelFactory
from anyblok.tests.conftest import init_registry_with_bloks, reset_db


# TODO Json, Password, Enum, JsonRelated
# TODO Forbid Sequence, Function,
# TODO Many2One, One2Many (1pk and 2 pk), forbid backref
# TODO One2Many
# TODO Many2Many
# TODO test main model and identity model with 2 pk
# TODO test with nullable=False 1 column and 2 columns
# TODO find a better way to declare identity model
# TODO find a good solution to select a fallback identity instance (lang)


register = Declarations.register
Model = Declarations.Model


def funct_related_model(ColumnType=None, **kwargs):

    @Declarations.register(Declarations.Model)
    class Project:

        id = Integer(primary_key=True)

    @register(Model, factory=RelatedModelFactory)
    class Test:

        @classmethod
        def define_related_models(cls):
            res = super().define_related_models()
            res.update({
                'project': {
                    'model': cls.anyblok.Project,
                },
            })
            return res

        id = Integer(primary_key=True)
        other = Related(field=ColumnType(**kwargs), identity='project')


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
    # (Enum, 'foo', 'bar', 'foo-bar', {'enum_cls': MyTestEnum}),
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
    # (Json, {'name': 'foo'}, {'name': 'bar'}, {'name': 'foo-bar'}, {}),
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
def registry_related_model(request, bloks_loaded, column_definition):  # noqa F811
    reset_db()
    column, value1, value2, value3, kwargs = column_definition
    registry = init_registry_with_bloks(
        ["furetui"], funct_related_model,
        ColumnType=column, **kwargs
    )
    request.addfinalizer(registry.close)
    return registry


class TestRelateModel:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_related_model, column_definition):
        registry = registry_related_model
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

    def test_insert(self, registry_related_model, column_definition):
        registry = registry_related_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project3):
            registry.Test.insert(other=value3)

    def test_insert_without_context(self, registry_related_model,
                                    column_definition):
        registry = registry_related_model
        column, value1, value2, value3, kwargs = column_definition
        with pytest.raises(FieldException):
            registry.Test.insert(other=value3)

    def test_get(self, registry_related_model, column_definition):
        registry = registry_related_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project1):
            assert self.test.other == value1

    def test_get_without_context(self, registry_related_model):
        with pytest.raises(FieldException):
            self.test.other

    def test_set_existing_value(self, registry_related_model,
                                column_definition):
        registry = registry_related_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project2):
            assert self.test.other == value2
            self.test.other = value3
            assert self.test.other == value3

    def test_set_new_value(self, registry_related_model, column_definition):
        registry = registry_related_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project3):
            assert not self.test.other
            self.test.other = value3
            assert self.test.other == value3

    def test_set_without_context(self, registry_related_model):
        with pytest.raises(FieldException):
            self.test.other = 'bar2'

    def test_del(self, registry_related_model, column_definition):
        registry = registry_related_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project1):
            assert self.test.other == value1
            del self.test.other
            assert not self.test.other

    def test_del_without_context(self, registry_related_model):
        with pytest.raises(FieldException):
            del self.test.other

    def test_expr(self, registry_related_model, column_definition):
        registry = registry_related_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project1):
            assert self.test is registry.Test.query().filter_by(
                other=value1).one()

    def test_expr_with_another_context(self, registry_related_model,
                                       column_definition):
        registry = registry_related_model
        column, value1, value2, value3, kwargs = column_definition
        with registry.Project.context.set(project=self.project2):
            assert registry.Test.query().filter_by(
                other=value1).one_or_none() is None

    def test_expr_without_context(self, registry_related_model,
                                  column_definition):
        registry = registry_related_model
        column, value1, value2, value3, kwargs = column_definition
        with pytest.raises(FieldException):
            registry.Test.query().filter_by(other=value1).one_or_none()
