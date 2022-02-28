from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy import and_, or_, select
from anyblok.field import Field, FieldException, Function
from anyblok.column import Sequence
from anyblok.relationship import Many2Many, Many2One, One2One, One2Many


class Many2OneComparator(Comparator):

    def __init__(self, fields, expression):
        self.fields = fields
        super().__init__(expression)

    def eq_op(self, subquery, m2o):
        expr = [
            getattr(subquery.c, f1) == getattr(m2o, f2)
            for f1, f2 in self.fields
        ]
        if len(expr) == 1:
            expr = expr[0]
        else:
            expr = and_(*expr)

        return expr

    def __eq__(self, m2o):
        clause = self.__clause_element__().subquery(name='subquery')
        return select(self.eq_op(clause, m2o))

    def is_(self, m2o):
        return self == m2o

    def __ne__(self, m2o):
        clause = self.__clause_element__().subquery(name='subquery')
        return select(~self.eq_op(clause, m2o))

    def is_not(self, m2o):
        return self != m2o

    def in_op(self, subquery, m2os):
        if len(self.fields) == 1:
            expr = getattr(subquery.c, self.fields[0][0]).in_(
                [getattr(m2o, self.fields[0][1]) for m2o in m2os])
        else:
            expr = [self.eq_op(subquery, m2o) for m2o in m2os]
            if len(expr) == 1:
                expr = expr[0]
            else:
                expr = or_(*expr)

        return expr

    def in_(self, m2os):
        clause = self.__clause_element__().subquery(name='subquery')
        expr = self.in_op(clause, m2os)
        return select(expr)

    def notin(self, m2os):
        clause = self.__clause_element__().subquery(name='subquery')
        expr = self.in_op(clause, m2os)
        return select(~expr)


class Contextual(Field):
    """ Json Contextual Field

    ::

        from anyblok.declarations import Declarations
        from anyblok_furetui.field import Contextual
        from anyblok.column import String


        @Declarations.register(Declarations.Model)
        class Project:

            code = String(primary_key=True)


        @Declarations.register(
            Declarations.Model,
            factory=ContextualModelFactory
        )
        class Test:

            @classmethod
            def define_contextual_models(cls):
                res = super().define_contextual_models()
                res.update({
                    'project': {
                        'model': cls.anyblok.Project,
                        'context': 'project',  # by default the key of dict
                        'context_adapter': lambda x: x
                        # by default return context
                    },
                })
                return res

            code = Contextual(
                field=String(),
                identity='project',
            )

    """
    def __init__(self, field=None, identity=None):
        self.field = field
        self.identity = identity

        for f in ['field', 'identity']:
            if getattr(self, f) is None:
                raise FieldException(
                    f"'{f}' is a required attribute for Contextual"
                )

        if isinstance(
            self.field,
            (Function, Sequence, One2One, One2Many, Many2Many)
        ):
            raise FieldException(
                f"'{f}' could not be {self.field.__class__}"
            )

        if (
            isinstance(self.field, Many2One) and
            self.field.kwargs.get('backref')
        ):
            raise FieldException(
                f"'{f}' could not have one2many attribute"
            )

        super(Contextual, self).__init__()

    def get_fget(self):
        def fget(model_self):
            identity_values = model_self.get_identity_entries(self.identity)

            if not identity_values['context']:
                raise FieldException('No valid context')

            o2m = identity_values['one2many']
            entry = o2m.filter_by(**identity_values['filter']).one_or_none()

            if entry is None:
                return identity_values['default']

            return getattr(entry, self.fieldname)

        return fget

    def get_fset(self):
        def fset(model_self, value):
            identity_values = model_self.get_identity_entries(self.identity)

            if not identity_values['context']:
                raise FieldException('No valid context')

            o2m = identity_values['one2many']
            entry = o2m.filter_by(**identity_values['filter']).one_or_none()

            if entry is None:
                values = {
                    self.fieldname: value,
                    'relate': model_self,
                }
                values.update(identity_values['filter'])
                entry = identity_values['Model'](**values)
                model_self.anyblok.session.add(entry)
            else:
                entry.update(**{self.fieldname: value})

        return fset

    def get_fdel(self):
        def fdel(model_self):
            identity_values = model_self.get_identity_entries(self.identity)

            if not identity_values['context']:
                raise FieldException('No valid context')

            o2m = identity_values['one2many']
            entry = o2m.filter_by(**identity_values['filter']).one_or_none()
            if entry is not None:
                setattr(entry, self.fieldname, None)

        return fdel

    def get_fexpr(self):
        def fexpr(cls):
            res = cls.define_contextual_models()[self.identity]
            context_adapter = res.get('context_adapter', lambda x: x)
            context = context_adapter(
                cls.context.get(res.get('context', self.identity)))

            if not context:
                raise FieldException('No valid context')

            Model = getattr(cls, self.identity.capitalize())

            filters = [getattr(Model, self.identity) == context]
            filters.extend([
                getattr(Model, x) == getattr(cls, x[len('relate_'):])
                for x in Model.loaded_columns
                if x.startswith("relate_")])

            return select(getattr(Model, self.fieldname)).filter(
                and_(*filters)).limit(1).label(self.fieldname)

        return fexpr

    def get_fcomparator(self):
        def fcomparator(cls):
            res = cls.define_contextual_models()[self.identity]
            context_adapter = res.get('context_adapter', lambda x: x)
            context = context_adapter(
                cls.context.get(res.get('context', self.identity)))

            if not context:
                raise FieldException('No valid context')

            Model = getattr(cls, self.identity.capitalize())

            filters = [getattr(Model, self.identity) == context]
            filters.extend([
                getattr(Model, x) == getattr(cls, x[len('relate_'):])
                for x in Model.loaded_columns
                if x.startswith("relate_")])

            fields = [
                (x, x[len(self.fieldname) + 1:])
                for x in Model.loaded_columns
                if x.startswith(f'{self.fieldname}_')]

            expr = select(Model).filter(and_(*filters)).limit(1)

            return Many2OneComparator(fields, expr)

        return fcomparator

    def get_sqlalchemy_mapping(self, registry, namespace, fieldname,
                               properties):
        """Return the property of the field

        :param registry: current registry
        :param namespace: name of the model
        :param fieldname: name of the field
        :param properties: properties known to the model
        """
        self.fieldname = fieldname
        self.format_label(fieldname)
        properties['loaded_fields'][fieldname] = self.label

        fget = self.get_fget()
        fset = self.get_fset()
        fdel = self.get_fdel()
        fexpr = self.get_fexpr()
        fcomparator = self.get_fcomparator()

        for funct in (fget, fset, fdel, fexpr, fcomparator):
            funct.__name__ = fieldname

        hybrid = hybrid_property(fget)
        hybrid = hybrid.setter(fset)
        hybrid = hybrid.deleter(fdel)
        if isinstance(self.field, Many2One):
            hybrid = hybrid.comparator(fcomparator)
        else:
            hybrid = hybrid.expression(fexpr)

        return hybrid

    def autodoc_get_properties(self):
        res = super().autodoc_get_properties()
        res.update({
            'field': self.field.autodoc_get_properties(),
            'identity': self.identity,
        })
        return res

    def update_description(self, registry, model, res):
        Field = registry.System.Field
        model2 = f"{model}.{self.identity.capitalize()}"
        field = Field.query().filter_by(model=model2, name=self.fieldname).one()
        res.update(field._description())
        res.update({'identity': self.identity, 'identity_model': model2})
