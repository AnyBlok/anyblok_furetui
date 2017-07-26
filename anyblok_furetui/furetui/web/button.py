from anyblok import Declarations
from anyblok.column import String, Integer, Selection
from anyblok.relationship import Many2One

register = Declarations.register
Model = Declarations.Model


@register(Model.Web.Action)
class Button:

    id = Integer(primary_key=True)
    action = Many2One(model=Model.Web.Action, one2many='buttons',
                      nullable=False)
    method = String(nullable=False)
    label = String(nullable=False)
    mode = Selection(selections=[('action', 'Action'), ('more', 'More')],
                     default='action', nullable=False)
