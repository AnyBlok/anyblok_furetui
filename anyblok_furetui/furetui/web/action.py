from anyblok import Declarations
from anyblok.column import String, Boolean, Integer

register = Declarations.register
Model = Declarations.Model


@register(Model.Web)
class Action:

    id = Integer(primary_key=True)
    model = String(foreign_key=Model.System.Model.use('name'), nullable=False)
    label = String(nullable=False)
    selected = Integer()
    add_delete = Boolean(default=True)
    add_new = Boolean(default=True)
    add_edit = Boolean(default=True)

    def render(self):
        views = [
            {
                'viewId': str(v.id),
                'type': v.mode.split('.')[-1],
                'unclickable': not v.selectable,
            }
            for v in self.views
        ]
        if not views:
            views = [
                {
                    'viewId': 'List-%d' % self.id,
                    'type': 'List',
                },
                {
                    'viewId': 'Form-%d' % self.id,
                    'type': 'Form',
                    'unclickable': True,
                },
            ]

        return {
            'type': 'UPDATE_ACTION',
            'actionId': str(self.id),
            'label': self.label,
            'views': views,
        }
