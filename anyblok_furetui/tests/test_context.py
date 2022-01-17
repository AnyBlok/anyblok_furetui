import pytest
from anyblok.tests.conftest import init_registry_with_bloks, reset_db


@pytest.fixture(scope="class")
def registry(request, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(["furetui"], None)
    request.addfinalizer(registry.close)
    return registry


class TestContext:

    @pytest.fixture(autouse=True)
    def transact(self, request, registry, clear_context):
        transaction = registry.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_base_cls(self, registry):
        System = registry.System
        assert len(System.context) == 0
        System.context.set(foo='bar')
        assert len(System.context) == 1
        assert System.context.get('foo') == 'bar'
        assert System.context['foo'] == 'bar'

    def test_base_instance(self, registry):
        model = registry.System.Model.query().first()
        assert len(model.context) == 0
        model.context.set(foo='bar')
        assert len(model.context) == 1
        assert model.context.get('foo') == 'bar'
        assert model.context['foo'] == 'bar'

    def test_iter(self, registry):
        System = registry.System
        assert len(System.context) == 0

        values = dict(foo='bar', bar='foo')
        System.context.set(**values)

        for x in System.context:
            assert System.context[x] == values[x]

    def test_context_manager(self, registry):
        System = registry.System
        assert len(System.context) == 0

        with System.context.set(foo='bar'):
            assert len(System.context) == 1
            assert System.context.get('foo') == 'bar'
            assert System.context['foo'] == 'bar'

        assert len(System.context) == 0
        assert System.context.get('foo') is None

        with pytest.raises(KeyError):
            System.context['foo']

    def test_setitem(self, registry):
        System = registry.System
        with pytest.raises(TypeError):
            System.context['foo'] = 'bar'

    def test_setdefault(self, registry):
        System = registry.System
        with pytest.raises(TypeError):
            System.context.setdefault('foo', 'bar')

    def test_update(self, registry):
        System = registry.System
        with pytest.raises(TypeError):
            System.context.update({'foo': 'bar'})

    def test_del(self, registry):
        System = registry.System
        System.context.set(foo='bar')
        with pytest.raises(TypeError):
            del System.context['foo']

    def test_clear(self, registry):
        System = registry.System
        System.context.set(foo='bar')
        with pytest.raises(TypeError):
            System.context.clear()

    def test_pop(self, registry):
        System = registry.System
        System.context.set(foo='bar')
        with pytest.raises(TypeError):
            System.context.pop()

    def test_popitem(self, registry):
        System = registry.System
        System.context.set(foo='bar')
        with pytest.raises(TypeError):
            System.context.popitem('foo')
