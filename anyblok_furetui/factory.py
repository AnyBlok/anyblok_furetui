from sqlalchemy.orm import relationship
from anyblok.model.factory import ModelFactory, has_sql_fields
from anyblok.model import Model
from anyblok.column import Integer
from anyblok.relationship import Many2One
from anyblok.field import FieldException
from anyblok.common import TypeList
from .field import Contextual


class ContextualMixin:

    @classmethod
    def define_contextual_models(cls):
        return {}

    def get_identity_entries(self, identity):
        res = self.__class__.define_contextual_models()[identity]
        context_adapter = res.get('context_adapter', lambda x: x)
        context = context_adapter(
            self.context.get(res.get('context', identity)))
        return {
            'context': context,
            'one2many': getattr(self, f'__{identity}'),
            'filter': {identity: context},
            'default': self.__class__.get_default_values().get(identity),
            'Model': getattr(self, identity.capitalize()),
        }

    @classmethod
    def insert(cls, **kwargs):
        related = {}
        values = kwargs.copy()

        lnfs = cls.anyblok.loaded_namespaces_first_step[cls.__registry_name__]
        for field in kwargs:
            if field in cls.loaded_contextual_fields:
                if lnfs[field].identity not in related:
                    related[lnfs[field].identity] = {}

                related[lnfs[field].identity][field] = values.pop(field)

        res = super(ContextualMixin, cls).insert(**values)

        for identity, values in related.items():
            identity_values = res.get_identity_entries(identity)
            if not identity_values['context']:
                raise FieldException('No valid context')

            values.update({identity: identity_values['context']})
            getattr(cls, identity.capitalize()).insert(
                relate=res, **values)

        return res


class ContextualModelFactory(ModelFactory):

    def declare_field_for(self, fieldname, field, properties,
                          transformation_properties):
        lnfs = self.registry.loaded_namespaces_first_step
        registry_name = properties['__registry_name__']
        lnfs[registry_name][fieldname] = field
        Model.declare_field(
            self.registry, fieldname, field,
            registry_name,
            properties,
            transformation_properties)

    def insert_core_bases(self, bases, properties):
        if has_sql_fields(bases):
            bases.append(ContextualMixin)

        super(ContextualModelFactory, self).insert_core_bases(bases, properties)

    def build_model(self, modelname, bases, properties):
        tmp_bases = [x for x in bases
                     if x is not self.registry.declarativebase]

        res = super(ContextualModelFactory, self).build_model(
            modelname, tmp_bases, properties)

        related_models = res.define_contextual_models()

        models = {}
        transformation_models = {}
        lnfs = self.registry.loaded_namespaces_first_step
        properties['loaded_contextual_fields'] = set()
        for fieldname in properties['loaded_fields']:
            field = lnfs[properties["__registry_name__"]][fieldname]
            if isinstance(field, Contextual):
                properties['loaded_contextual_fields'].add(fieldname)
                registry_name = (
                    f'{properties["__registry_name__"]}.'
                    f'{field.identity.capitalize()}')
                if field.identity not in models:
                    transformation_models[field.identity] = {}
                    tablename = (
                        f"{properties['__tablename__']}_{field.identity}"
                    )

                    lnfs[registry_name] = {
                        '__depends__': set(),
                        '__db_schema__': properties['__db_schema__'],
                        '__tablename__': tablename,
                    }

                    models[field.identity] = {
                        '__db_schema__': properties['__db_schema__'],
                        '__depends__': set(),
                        '__model_factory__': ModelFactory(
                            registry=self.registry),
                        '__registry_name__': registry_name,
                        '__tablename__': tablename,
                        'add_in_table_args': [],  # Add unicity
                        'hybrid_property_columns': [],
                        'loaded_columns': [],
                        'loaded_fields': {},
                    }

                    self.registry.call_plugins(
                        'initialisation_tranformation_properties',
                        models[field.identity],
                        transformation_models[field.identity])

                    self.declare_field_for(
                        'id',
                        Integer(primary_key=True),
                        models[field.identity],
                        transformation_models[field.identity],
                    )

                    self.declare_field_for(
                        'relate',
                        Many2One(model=properties['__registry_name__'],
                                 nullable=False),
                        models[field.identity],
                        transformation_models[field.identity],
                    )

                    self.declare_field_for(
                        field.identity,
                        Many2One(
                            model=related_models[field.identity]['model'],
                            nullable=False,
                        ),
                        models[field.identity],
                        transformation_models[field.identity],
                    )

                self.declare_field_for(
                    fieldname,
                    field.field,
                    models[field.identity],
                    transformation_models[field.identity],
                )

        for name, model_properties in models.items():
            bases_ = TypeList(
                Model, self.registry, model_properties['__registry_name__'],
                transformation_models[name])
            bases_.extend([x for x in self.registry.loaded_cores['SqlBase']])
            bases_.append(self.registry.declarativebase)
            bases_.extend([x for x in self.registry.loaded_cores['Base']])
            bases_.append(self.registry.registry_base)
            Model.insert_in_bases(
                self.registry, model_properties['__registry_name__'],
                bases_, transformation_models[name], model_properties)
            relate_modelname = f'{modelname}{name.capitalize()}'
            relate = type(
                relate_modelname,
                tuple(bases_),
                model_properties)
            properties[name.capitalize()] = relate
            self.registry.loaded_namespaces[
                model_properties['__registry_name__']] = relate

            primaryjoin = [
                f"{relate_modelname}.{x} == {modelname}.{x[len('relate_'):]}"
                for x in relate.loaded_columns
                if x.startswith('relate_')]
            properties[f"__{name}"] = relationship(
                relate,
                primaryjoin='and_(' + ', '.join(primaryjoin) + ')',
                lazy='dynamic',
                overlaps='__anyblok_field_relate')

        return super(ContextualModelFactory, self).build_model(
            modelname, bases, properties)
