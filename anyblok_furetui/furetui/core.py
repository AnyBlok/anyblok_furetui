from anyblok.declarations import Declarations
from ..core import SqlMixin


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


@Declarations.register(Declarations.Core)
class SqlViewBase(SqlMixin):

    @classmethod
    def furetui_insert(cls, **kwargs):
        raise Exception("View is not allowed to do this action")

    def furetui_update(self, **kwargs):
        raise Exception("View is not allowed to do this action")

    def furetui_delete(self):
        raise Exception("View is not allowed to do this action")
