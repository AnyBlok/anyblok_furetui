from anyblok import Declarations
from anyblok.column import Integer, String, Selection
from anyblok.relationship import Many2One

register = Declarations.register
Web = Declarations.Model.Web


@register(Web)
class Menu:

    id = Integer(primary_key=True)
    label = String(nullable=False)
    space = Many2One(model=Web.Space, one2many='menus',
                     foreign_key_options={'ondelete': 'cascade'})
    parent = Many2One(model='Model.Web.Menu', one2many='children',
                      foreign_key_options={'ondelete': 'cascade'})
    order = Integer(nullable=False, default=100)
    icon = String()
    position = Selection(
        selections=[('left', 'On the left'), ('right', 'On the right')])
    type = Selection(selections=[('client', 'Client'), ('action', 'Action')],
                     default='action', nullable=False)
    action = Many2One(model=Web.Action, one2many="menus")
    client = String()

    @classmethod
    def recMenu(cls, menus):
        res = []
        for menu in menus:
            actionId = ''
            if menu.type == 'client':
                actionId = menu.client
            elif menu.type == 'action':
                actionId = menu.action and menu.action.id or ''

            m = {
                'id': str(menu.id),
                'label': menu.label,
                'image': {'type': 'font-icon', 'value': menu.icon},
                'actionId': actionId,
                'submenus': [],
            }
            if menu.children:
                query = cls.query().filter(cls.parent == menu)
                query = query.order_by(cls.order)
                m['submenus'] = cls.recMenu(query.all())

            res.append(m)

        return res

    @classmethod
    def getMenusForSpace(cls, space, position):
        query = cls.query().filter(
            cls.space == space,
            cls.parent == None,  # noqa
            cls.position == position
        )
        query = query.order_by(cls.order)
        return cls.recMenu(query.all())
