from anyblok.environment import EnvironmentManager


__all__ = ['context', 'ImmutableContextDict']


class AttributeContextManager:

    def __init__(self, previous_context):
        self.previous_context = previous_context

    def __enter__(self):
        return EnvironmentManager.get(
            'context', default=ImmutableContextDict({}))

    def __exit__(self, type, value, traceback):
        EnvironmentManager.set('context', self.previous_context)


def _not_allowed(cls, *args, **kwargs):
    raise TypeError("Operation not allowed on ImmutableDict")


class ImmutableContextDict(dict):

    __slots__ = ()

    __setitem__ = _not_allowed
    __delitem__ = _not_allowed
    __ior__ = _not_allowed
    clear = _not_allowed
    pop = _not_allowed
    popitem = _not_allowed
    setdefault = _not_allowed
    update = _not_allowed

    def set(self, context=None, **kwargs):
        if context is None:
            context = {}

        previous_context = EnvironmentManager.get(
            'context', default=ImmutableContextDict({}))
        manager = AttributeContextManager(previous_context)
        ctx = previous_context.copy()
        ctx.update(context)
        ctx.update(kwargs)
        EnvironmentManager.set('context', ImmutableContextDict(ctx))
        return manager


def wrap_attribute(meth):

    def wrap(self, *a, **kw):
        context = EnvironmentManager.get(
            'context', default=ImmutableContextDict({}))
        return getattr(context, meth)(*a, **kw)

    return wrap


class ProxyContext:

    def __getattr__(self, key):
        context = EnvironmentManager.get(
            'context', default=ImmutableContextDict({}))
        return getattr(context, key)


for key in ('__str__', '__repr__', '__getitem__', '__len__', '__contains__',
            '__eq__', '__ge__', '__gt__', '__iter__', '__le__',
            '__lt__', '__ne__', '__or__', '__ror__'):
    setattr(ProxyContext, key, wrap_attribute(key))


context = ProxyContext()
