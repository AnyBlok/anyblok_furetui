from anyblok import Declarations
from anyblok.column import Integer, String, Text, Selection
from anyblok.relationship import Many2One


Web = Declarations.Model.Web


@Declarations.register(Web)
class Space:

    id = Integer(primary_key=True)
    label = String(nullable=False)
    icon = String()
    description = Text()
    type = Selection(selections=[('client', 'Client'), ('space', 'Space')],
                     default='space', nullable=False)
    order = Integer(nullable=False, default=100)
    category = Many2One(model="Model.Web.Space.Category", nullable=False)
    default_menu = Many2One(model='Model.Web.Menu')
    default_action = Many2One(model='Model.Web.Action')

    @classmethod
    def getSpaces(cls, params):
        values = []
        value = {
            'label': '',
            'image': {'type': 'font-icon', 'value': ''},
        }
        Category = cls.registry.Web.Space.Category
        for c in Category.query().order_by(Category.order).all():
            query = cls.query().filter(cls.category == c).order_by(cls.order)
            if query.count():
                categ = {
                    'id': str(c.id),
                    'label': c.label,
                    'image': {'type': 'font-icon', 'value': c.icon},
                    'values': [],
                }
                values.append(categ)
                for s in query.all():
                    categ['values'].append({
                        'id': str(s.id),
                        'label': s.label,
                        'description': s.description,
                        'type': s.type,
                        'image': {'type': 'font-icon', 'value': s.icon},
                    })

        if'route_params' in params and params['route_params'].get('spaceId'):
            space = cls.query().get(int(params['route_params']['spaceId']))
            value['label'] = space.label
            value['image']['value'] = space.icon
        else:
            value['label'] = values[0]['values'][0]['label']
            value['image'] = values[0]['values'][0]['image']

        return {
            'type': 'UPDATE_LEFT_MENU',
            'value': value,
            'values': values,
        }

    def getLeftMenus(self):
        Menu = self.registry.Web.Menu
        return Menu.getMenusForSpace(self, 'left')

    def getRightMenus(self):
        Menu = self.registry.Web.Menu
        return Menu.getMenusForSpace(self, 'right')


@Declarations.register(Web.Space)
class Category:

    id = Integer(primary_key=True)
    label = String(nullable=False)
    icon = String()
    order = Integer(nullable=False, default=100)
