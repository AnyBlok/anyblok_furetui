from anyblok.model.factory import BaseFactory
from anyblok.column import Integer
from anyblok.model import Model


class SingletonMixin:

    @classmethod
    def furetui_insert(cls, **kwargs):
        return cls.set(**kwargs)

    def furetui_update(self, **kwargs):
        return self.__class__.set(**kwargs)

    def furetui_delete(self):
        raise Exception('Delete is forbidden')

    @classmethod
    def get_default_values(cls, *a, **kw):
        self = cls.get()
        return {
            field: getattr(self, field)
            for field in cls.loaded_columns
        }

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

    def declare_field_for(self, fieldname, field, properties):
        lnfs = self.registry.loaded_namespaces_first_step
        registry_name = properties['__registry_name__']
        lnfs[registry_name][fieldname] = field
        Model.declare_field(
            self.registry, fieldname, field,
            registry_name,
            properties,
            {})

    def insert_core_bases(self, bases, properties):
        bases.append(SingletonMixin)
        bases.extend([x for x in self.registry.loaded_cores['SqlBase']])
        bases.append(self.registry.declarativebase)
        bases.extend([x for x in self.registry.loaded_cores['Base']])

    def build_model(self, modelname, bases, properties):
        self.declare_field_for('id', Integer(primary_key=True), properties)
        return type(modelname, tuple(bases), properties)
