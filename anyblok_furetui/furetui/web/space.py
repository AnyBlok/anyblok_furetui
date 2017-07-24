from anyblok import Declarations
from anyblok.column import Integer, String, Text, Selection
from anyblok.relationship import Many2One


@Declarations.register(Declarations.Model.Web)
class Space:

    id = Integer(primary_key=True)
    label = String(nullable=False)
    icon = String()
    description = Text()
    type = Selection(selections=[('client', 'Client'), ('space', 'Space')],
                     default='space', nullable=False)
    order = Integer(nullable=False, default=100)
    category = Many2One(model="Model.Web.Space.Category", nullable=False)
    menu_position = Selection(selections=[('left', 'On the left'),
                                          ('right', 'On the right')],
                              default='left', nullable=False)
    # default_menu = Many2One(model='Model.UI.Menu')
    # default_action = Many2One(model='Model.UI.Action')


@Declarations.register(Declarations.Model.Web.Space)
class Category:

    id = Integer(primary_key=True)
    label = String(nullable=False)
    icon = String()
    order = Integer(nullable=False, default=100)
