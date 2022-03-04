from anyblok.declarations import Declarations
from anyblok_furetui import exposed_method
from ..context import context
from ..core import SqlMixin


@Declarations.register(Declarations.Core)
class Base:

    context = context


@Declarations.register(Declarations.Core)
class SqlBase(SqlMixin):

    @classmethod
    def furetui_insert(cls, **kwargs):
        res = cls.insert(**kwargs)
        if res is None:
            raise Exception('No instance returned by %r.insert' % cls)

        return res

    def furetui_update(self, **kwargs):
        return self.update(**kwargs)

    def furetui_delete(self):
        return self.delete()

    @classmethod
    def get_default_values(
        cls,
        request=None,
        authenticated_userid=None,
        resource=None,
        **data
    ):
        return {
            x.name: (
                x.default.arg(None)
                if callable(x.default.arg)
                else x.default.arg
            )
            for x in cls.__table__.columns
            if x.default
        }

    @exposed_method(
        is_classmethod=True,
        request="request",
        authenticated_userid="authenticated_userid",
        resource="resource",
        permission="create"
    )
    def default_values(
        cls,
        request=None,
        authenticated_userid=None,
        resource=None,
        uuid=None,
    ):
        """This method aims to be called by client on model before creating
        a new object to define it's default values.

        It return a dict with default values.
        """
        res = []
        values = cls.get_default_values(
            request=request, authenticated_userid=authenticated_userid,
            resource=resource, uuid=uuid)
        fd = cls.fields_description()
        for key, value in values.items():
            if fd[key]['type'] in ('Many2One', 'One2One'):
                res.extend([
                    {
                        "type": "UPDATE_CHANGE",
                        "model": cls.__registry_name__,
                        "uuid": uuid,
                        "fieldname": key,
                        "value": value.to_primary_keys(),
                    },
                    {
                        "type": "UPDATE_DATA",
                        "model": value.__registry_name__,
                        "pk": value.to_primary_keys(),
                        "data": {
                            **{x: getattr(value, x)
                               for x in value.get_display_fields()},
                            **value.to_primary_keys(),
                        },
                    },
                ])
            elif fd[key]['type'] in ('One2Many', 'Many2Many'):
                pass
            else:
                res.append({
                    "type": "UPDATE_CHANGE",
                    "model": cls.__registry_name__,
                    "uuid": uuid,
                    "fieldname": key,
                    "value": value,
                })
        return res


@Declarations.register(Declarations.Core)
class SqlViewBase(SqlMixin):

    @classmethod
    def furetui_insert(cls, **kwargs):
        raise Exception("View is not allowed to do this action")

    def furetui_update(self, **kwargs):
        raise Exception("View is not allowed to do this action")

    def furetui_delete(self):
        raise Exception("View is not allowed to do this action")
