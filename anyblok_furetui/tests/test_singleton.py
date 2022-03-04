import pytest
from anyblok import Declarations
from anyblok.column import String
from anyblok.tests.conftest import init_registry_with_bloks, reset_db
from anyblok_furetui.factory import SingletonModelFactory


register = Declarations.register
Model = Declarations.Model


def simple_model():

    @register(Model, factory=SingletonModelFactory)
    class Conf:
        other = String(nullable=False, default='Test')
        name = String()


@pytest.fixture(scope="class")
def registry_simple_model(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(["furetui"], simple_model)
    request.addfinalizer(registry.close)
    return registry


class TestSingletonModel:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry_simple_model):
        registry = registry_simple_model
        transaction = registry.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_get(self, registry_simple_model):
        registry = registry_simple_model
        assert registry.Conf.get().other == 'Test'
        assert registry.Conf.get().name is None

    def test_set(self, registry_simple_model):
        registry = registry_simple_model
        assert registry.Conf.get().other == 'Test'
        assert registry.Conf.get().name is None
        registry.Conf.set(name='foo')
        assert registry.Conf.get().other == 'Test'
        assert registry.Conf.get().name == 'foo'
