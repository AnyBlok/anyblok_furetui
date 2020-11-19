import pytest
from anyblok import Declarations
from anyblok_furetui import exposed_method
from anyblok.column import (
    Boolean, Json, String, BigInteger, Text, Selection,
    Date, DateTime, Time, Interval, Decimal, Float, LargeBinary, Integer,
    Sequence, Color, Password, UUID, URL, PhoneNumber, Email, Country,
    TimeStamp, Enum)
from anyblok.tests.conftest import init_registry_with_bloks, reset_db
from anyblok.tests.test_column import (
    simple_column, has_cryptography, has_passlib, has_colour, has_furl,
    has_phonenumbers, has_pycountry)
from ..testing import TmpTemplate


@pytest.fixture(scope="class")
def registry_Boolean(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], simple_column, ColumnType=Boolean)
    request.addfinalizer(registry.close)
    return registry


class TestResourceList:

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
