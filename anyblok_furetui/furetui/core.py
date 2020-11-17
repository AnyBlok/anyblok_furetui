from anyblok.declarations import Declarations, classmethod_cache


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
        return cls.insert(**kwargs)

    def furetui_update(self, **kwargs):
        return self.update(**kwargs)

    def furetui_delete(self):
        return self.delete()


@Declarations.register(Declarations.Core)
class SqlViewBase(SqlMixin):

    @classmethod
    def furetui_insert(cls, **kwargs):
        raise Exception("View is not allowed to do this action")

    def furetui_update(self, **kwargs):
        raise Exception("View is not allowed to do this action")

    def furetui_delete(self):
        raise Exception("View is not allowed to do this action")
