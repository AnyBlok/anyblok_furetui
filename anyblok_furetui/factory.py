from anyblok.model.factory import BaseFactory
from anyblok.column import Integer
from .core import SqlMixin


class SingletonMixin(SqlMixin):

    is_sql = True

    id = Integer(primary_key=True)

    @classmethod
    def furetui_insert(cls, **kwargs):
        res = cls.insert(**kwargs)
        if res is None:
            raise Exception('No instance returned by %r.insert' % cls)

        return res

    def furetui_update(self, **kwargs):
        return self.__class__.set(**kwargs)

    def furetui_delete(self):
        return self.delete()

    @classmethod
    def get(cls):
        singleton = cls.anyblok.query(cls).one_or_none()
        if singleton is None:
            singleton = cls()
            cls.anyblok.add(singleton)
            cls.anyblok.flush()

        return singleton

    @classmethod
    def set(cls, **kwargs):
        singleton = cls.anyblok.query(cls).one_or_none()
        if singleton is None:
            singleton = cls(**kwargs)
            cls.anyblok.add(singleton)
            cls.anyblok.flush()
            return singleton

        for k, v in kwargs.items():
            setattr(singleton, k, v)
            cls.anyblok.flush()

        return singleton


class SingletonModelFactory(BaseFactory):

    def insert_core_bases(self, bases, properties):
        bases.append(SingletonMixin)
        bases.append(self.registry.declarativebase)
        bases.extend([x for x in self.registry.loaded_cores['Base']])

    def build_model(self, modelname, bases, properties):
        return type(modelname, tuple(bases), properties)
