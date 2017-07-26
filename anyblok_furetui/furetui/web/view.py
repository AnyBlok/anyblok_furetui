from anyblok import Declarations
from anyblok.column import Integer, Boolean, String, Selection
from anyblok.relationship import Many2One


register = Declarations.register
Model = Declarations.Model
Mixin = Declarations.Mixin


@register(Mixin)
class ViewType:

    mode = Selection(selections='get_mode_choices', nullable=False)

    @classmethod
    def get_mode_choices(cls):
        """ Return the View type available

        :rtype: dict(registry name: label)
        """
        return {
            'Model.Web.View.List': 'List view',
            'Model.Web.View.Thumbnail': 'Thumbnails view',
            'Model.Web.View.Form': 'Form view',
        }


@register(Model.Web)
class View(Mixin.ViewType):

    id = Integer(primary_key=True)
    order = Integer(sequence='web__view_order_seq', nullable=False)
    selectable = Boolean(default=False)
    action = Many2One(model=Model.Web.Action, one2many='views', nullable=False)
    template = String(nullable=False)
    add_delete = Boolean(default=True)
    add_new = Boolean(default=True)
    add_edit = Boolean(default=True)
    on_change = Many2One(model='Model.Web.View')

    def render(self):
        return self.registry.get(self.mode)().render(self)

    @classmethod
    def bulk_render(cls, actionId=None, viewId=None, **kwargs):
        action = cls.registry.Web.Action.query().get(int(actionId))
        return cls.registry.get('Model.Web.View.' + viewId.split('-')[0]).bulk_render(
            action, viewId)


@register(Mixin)  # noqa
class View:
    mode_name = None

    def render(self, view):
        return {
            'type': 'UPDATE_VIEW',
            'viewId': str(view.id),
            'viewType': self.mode_name,
            'creatable': view.action.add_new and view.add_new or False,
            'deletable': view.action.add_delete and view.add_delete or False,
            'editable': view.action.add_edit and view.add_edit or False,
            'model': view.action.model,
        }

    @classmethod
    def bulk_render(cls, action, viewId):
        return {
            'type': 'UPDATE_VIEW',
            'viewId': viewId,
            'viewType': cls.mode_name,
            'creatable': action.add_new or False,
            'deletable': action.add_delete or False,
            'editable': action.add_edit or False,
            'model': action.model,
        }


@register(Model.Web.View)
class List(Mixin.View):
    "List View"

    mode_name = 'List'

    @classmethod
    def field_for_(cls, field):
        res = {
            'name': field['id'],
            'label': field['label'],
            'component': 'furet-ui-list-field-' + field['type'].lower(),
        }
        for k in field:
            if k not in ('id', 'label', 'type', 'nullable', 'primary_key',
                         'model'):
                res[k] = field[k]

        return res

    @classmethod
    def field_for_BigInteger(cls, field):
        f = field.copy()
        f['type'] = 'Integer'
        return cls.field_for_(f)

    @classmethod
    def field_for_SmallInteger(cls, field):
        f = field.copy()
        f['type'] = 'Integer'
        return cls.field_for_(f)

    @classmethod
    def field_for_LargeBinary(cls, field):
        f = field.copy()
        f['type'] = 'file'
        return cls.field_for_(f)

    @classmethod
    def field_for_Sequence(cls, field):
        f = field.copy()
        f['type'] = 'string'
        res = cls.field_for_(f)
        res['readonly'] = True
        return res

    @classmethod
    def field_for_Selection(cls, field):
        f = field.copy()
        if isinstance(f['selections'], list):
            f['selections'] = dict(f['selections'])

        return cls.field_for_(f)

    @classmethod
    def field_for_UUID(cls, field):
        f = field.copy()
        f['type'] = 'string'
        res = cls.field_for_(f)
        res['readonly'] = True
        return res

    @classmethod
    def bulk_render(cls, action, viewType):
        res = super(List, cls).bulk_render(action, viewType)
        Model = cls.registry.get(action.model)
        fields = cls.registry.System.Column.query().filter_by(
            model=action.model).all().name
        headers = []
        search = []
        for field_name, field in Model.fields_description(fields).items():
            meth = 'field_for_' + field['type']
            if hasattr(cls, meth):
                headers.append(getattr(cls, meth)(field))
            else:
                headers.append(cls.field_for_(field))

            search.append({
                'key': field_name,
                'label': field['label'],
                'type': 'search',
            })

        res.update({
            'selectable': False,
            'onSelect': 'Form-%d' % action.id,
            'headers': headers,
            'search': search,
            'buttons': [],
            'onSelect_buttons': [],
            'fields': fields,
        })
        return res


@register(Model.Web.View)
class Thumbnail(Mixin.View):
    "Thumbnail View"

    mode_name = 'Thumbnail'


@register(Model.Web.View)
class Form(Mixin.View):
    "Form View"

    mode_name = 'Form'
