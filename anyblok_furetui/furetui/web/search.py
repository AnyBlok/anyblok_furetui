from anyblok import Declarations
from anyblok.column import String, Integer, Selection
from anyblok.relationship import Many2One

register = Declarations.register
Model = Declarations.Model


@register(Model.Web.Action)
class Search:

    id = Integer(primary_key=True)
    action = Many2One(model=Model.Web.Action, one2many='searchs')
    view = Many2One(model=Model.Web.View, one2many='searchs')
    fieldname = String(nullable=False)
    path = String()
    label = String()
    type = Selection(
        selections=[('search', 'Search on specific key'),
                    ('filter', 'Defined search')],
        default='search', nullable=False
    )

    def format_for_furetui(self, model):
        if self.path:
            key = self.path + '.' + self.fieldname
        else:
            key = self.fieldname

        Model = self.registry.get(model)
        for k in key.split('.')[:-1]:
            Model = Model.getRemoteModelFor(k)

        label = Model.fields_description(
            self.fieldname)[self.fieldname]['label']

        return {
            'fieldname': self.fieldname,
            'key': key,
            'model': Model.__registry_name__,
            'label': label,
            'type': self.type,
        }

    @classmethod
    def get_from_action(cls, action):
        res = []
        for search in action.searchs:
            res.append(search.format_for_furetui(action.model))
        return res

    @classmethod
    def get_from_view(cls, view):
        res = cls.get_from_action(view.action)
        for search in view.searchs:
            res.append(search.format_for_furetui(view.action.model))
        return res
