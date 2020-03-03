from anyblok.declarations import Declarations, classmethod_cache


class SqlMixin:

    _display_fields = None
    _filter_fields = None

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
        if cls._display_fields is not None:
            if isinstance(cls._display_fields, (list, set, tuple)):
                return cls._display_fields

            return [cls._display_fields]

        for field in ('label', 'title', 'name', 'code'):
            if hasattr(cls, field):
                return [field]

        return cls.get_primary_keys()


@Declarations.register(Declarations.Core)
class SqlBase(SqlMixin):
    pass


@Declarations.register(Declarations.Core)
class SqlViewBase(SqlMixin):
    pass
