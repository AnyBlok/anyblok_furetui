import pytest


@pytest.mark.usefixtures("rollback_registry")
class TestContext:

    @pytest.fixture(autouse=True)
    def transact(self, request, rollback_registry, clear_context):
        transaction = rollback_registry.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_base_cls(self, rollback_registry):
        System = rollback_registry.System
        assert len(System.context) == 0
        System.context.set(foo='bar')
        assert len(System.context) == 1
        assert System.context.get('foo') == 'bar'
        assert System.context['foo'] == 'bar'

    def test_base_instance(self, rollback_registry):
        model = rollback_registry.System.Model.query().first()
        assert len(model.context) == 0
        model.context.set(foo='bar')
        assert len(model.context) == 1
        assert model.context.get('foo') == 'bar'
        assert model.context['foo'] == 'bar'

    def test_iter(self, rollback_registry):
        System = rollback_registry.System
        assert len(System.context) == 0

        values = dict(foo='bar', bar='foo')
        System.context.set(**values)

        for x in System.context:
            assert System.context[x] == values[x]

    def test_context_manager(self, rollback_registry):
        System = rollback_registry.System
        assert len(System.context) == 0

        with System.context.set(foo='bar'):
            assert len(System.context) == 1
            assert System.context.get('foo') == 'bar'
            assert System.context['foo'] == 'bar'

        assert len(System.context) == 0
        assert System.context.get('foo') is None

        with pytest.raises(KeyError):
            System.context['foo']

    def test_setitem(self, rollback_registry):
        System = rollback_registry.System
        with pytest.raises(TypeError):
            System.context['foo'] = 'bar'

    def test_setdefault(self, rollback_registry):
        System = rollback_registry.System
        with pytest.raises(TypeError):
            System.context.setdefault('foo', 'bar')

    def test_update(self, rollback_registry):
        System = rollback_registry.System
        with pytest.raises(TypeError):
            System.context.update({'foo': 'bar'})

    def test_del(self, rollback_registry):
        System = rollback_registry.System
        System.context.set(foo='bar')
        with pytest.raises(TypeError):
            del System.context['foo']

    def test_clear(self, rollback_registry):
        System = rollback_registry.System
        System.context.set(foo='bar')
        with pytest.raises(TypeError):
            System.context.clear()

    def test_pop(self, rollback_registry):
        System = rollback_registry.System
        System.context.set(foo='bar')
        with pytest.raises(TypeError):
            System.context.pop()

    def test_popitem(self, rollback_registry):
        System = rollback_registry.System
        System.context.set(foo='bar')
        with pytest.raises(TypeError):
            System.context.popitem('foo')
