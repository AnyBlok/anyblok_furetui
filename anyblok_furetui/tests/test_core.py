import pytest
from anyblok import Declarations
from anyblok.column import Integer, String
from anyblok.tests.conftest import init_registry_with_bloks, reset_db
from anyblok_pyramid_rest_api.adapter import Adapter
from anyblok.tests.test_view import simple_view


register = Declarations.register
Model = Declarations.Model


def simple_model():

    @register(Model)
    class Test:
        id = Integer(primary_key=True)
        other = String()
        name = String()


def model_on_pks():

    @register(Model)
    class Test:
        id = Integer(primary_key=True)
        other = String()


def model_with_display_fields():

    @register(Model)
    class Test:
        _display_fields = 'other'

        id = Integer(primary_key=True)
        other = String()
        name = String()


def model_with_display_fields_2():

    @register(Model)
    class Test:
        _display_fields = ['other']

        id = Integer(primary_key=True)
        other = String()
        name = String()


def model_with_filter_fields():

    @register(Model)
    class Test:
        _filter_fields = 'other'

        id = Integer(primary_key=True)
        other = String()
        name = String()


class FuretUIAdapter(Adapter):
    pass


def model_with_adapter():

    @register(Model)
    class Test:

        FuretUIAdapter = FuretUIAdapter

        id = Integer(primary_key=True)
        other = String()
        name = String()


PARAMS = [
    {
        'funct': simple_model,
        'display_fields': ['name'],
        'filter_fields': ['name'],
        'adapter': None,
    },
    {
        'funct': model_on_pks,
        'display_fields': ['id'],
        'filter_fields': ['id'],
        'adapter': None,
    },
    {
        'funct': model_with_display_fields,
        'display_fields': ['other'],
        'filter_fields': ['other'],
        'adapter': None,
    },
    {
        'funct': model_with_display_fields_2,
        'display_fields': ['other'],
        'filter_fields': ['other'],
        'adapter': None,
    },
    {
        'funct': model_with_filter_fields,
        'display_fields': ['name'],
        'filter_fields': ['other'],
        'adapter': None,
    },
    {
        'funct': model_with_adapter,
        'display_fields': ['name'],
        'filter_fields': ['name'],
        'adapter': FuretUIAdapter,
    },
]


@pytest.fixture(scope="class", params=PARAMS)
def registry_core(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(["furetui"], request.param['funct'])
    request.addfinalizer(registry.close)
    return registry, request.param


class TestCore:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_core):
        registry, _ = registry_core
        transaction = registry.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get_display_fields(self, registry_core):
        registry, param = registry_core
        fields = param['display_fields']
        assert registry.Test.get_display_fields() == fields

    def test_get_filter_fields(self, registry_core):
        registry, param = registry_core
        fields = param['filter_fields']
        assert registry.Test.get_filter_fields() == fields

    def test_get_furetui_adapter(self, registry_core):
        registry, param = registry_core
        adapter = param['adapter']
        assert registry.Test.adapter_ is None

        if adapter is None:
            assert registry.Test.get_furetui_adapter() is None
            assert registry.Test.adapter_ is None
        else:
            ad = registry.Test.get_furetui_adapter()
            assert ad.__class__ == adapter
            assert registry.Test.adapter_ is ad

    def test_furetui_insert(self, registry_core):
        registry, param = registry_core
        assert registry.Test.query().filter_by(other='test').count() == 0
        registry.Test.furetui_insert(other='test')
        assert registry.Test.query().filter_by(other='test').count() == 1

    def test_furetui_update(self, registry_core):
        registry, param = registry_core
        test = registry.Test.insert()
        assert registry.Test.query().filter_by(other='test').count() == 0
        test.furetui_update(other='test')
        assert registry.Test.query().filter_by(other='test').count() == 1

    def test_furetui_delete(self, registry_core):
        registry, param = registry_core
        test = registry.Test.insert(other='test')
        assert registry.Test.query().filter_by(other='test').count() == 1
        test.furetui_delete()
        assert registry.Test.query().filter_by(other='test').count() == 0


@pytest.fixture(scope="class")
def registry_core_view(request, bloks_loaded):
    reset_db()
    registry = init_registry_with_bloks(['furetui'], simple_view)
    request.addfinalizer(registry.close)
    registry.T1.insert(code='test1', val=1)
    registry.T2.insert(code='test1', val=2)
    registry.T1.insert(code='test2', val=3)
    registry.T2.insert(code='test2', val=4)
    return registry


class TestCoreView:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_core_view):
        transaction = registry_core_view.begin_nested()
        request.addfinalizer(transaction.rollback)

    def test_get_display_fields(self, registry_core_view):
        assert registry_core_view.TestView.get_display_fields() == ['code']

    def test_get_filter_fields(self, registry_core_view):
        assert registry_core_view.TestView.get_filter_fields() == ['code']

    def test_get_furetui_adapter(self, registry_core_view):
        assert registry_core_view.TestView.adapter_ is None
        assert registry_core_view.TestView.get_furetui_adapter() is None

    def test_furetui_insert(self, registry_core_view):
        with pytest.raises(Exception):
            registry_core_view.TestView.furetui_insert(code='test')

    def test_furetui_update(self, registry_core_view):
        test = registry_core_view.TestView.query().first()
        with pytest.raises(Exception):
            test.furetui_update(other='test')

    def test_furetui_delete(self, registry_core_view):
        test = registry_core_view.TestView.query().first()
        with pytest.raises(Exception):
            test.furetui_delete()
