from anyblok.declarations import Declarations, classmethod_cache
from anyblok_furetui import exposed_method
from ..context import context


@Declarations.register(Declarations.Core)
class Base:

    context = context


class SqlMixin:

    _display_fields = None
    _filter_fields = None
    FuretUIAdapter = None
    adapter_ = None

    @classmethod_cache()
    def get_display_fields(cls):
        if cls._display_fields is not None:
            if isinstance(cls._display_fields, (list, set, tuple)):
                return cls._display_fields

            return [cls._display_fields]

        for field in ('label', 'title', 'name', 'code'):
            if hasattr(cls, field):
                return [field]

        return cls.get_primary_keys()

    @classmethod_cache()
    def get_filter_fields(cls):
        filter_fields = cls._filter_fields or cls._display_fields
        if filter_fields is not None:
            if isinstance(filter_fields, (list, set, tuple)):
                return filter_fields

            return [filter_fields]

        for field in ('label', 'title', 'name', 'code'):
            if hasattr(cls, field):
                return [field]

        return cls.get_primary_keys()

    @classmethod
    def get_furetui_adapter(cls):
        if cls.FuretUIAdapter is None:
            return None

        if not cls.adapter_:
            cls.adapter_ = cls.FuretUIAdapter(cls.registry, cls)
            cls.adapter_.load_decorators()

        return cls.adapter_


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
