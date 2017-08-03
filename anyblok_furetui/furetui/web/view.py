from anyblok import Declarations
from anyblok.column import Integer, Boolean, String, Selection
from anyblok.relationship import Many2One
from lxml import etree, html


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
    action = Many2One(model=Model.Web.Action, one2many='views', nullable=False)
    template = String(nullable=False)
    add_delete = Boolean(default=True)
    add_new = Boolean(default=True)
    add_edit = Boolean(default=True)
    on_change = Many2One(model='Model.Web.View')
    # list view
    selectable = Boolean(default=False)
    # thumbnail view
    border_fieldcolor = String(size=256)
    background_fieldcolor = String(size=256)

    def render(self):
        return self.registry.get(self.mode)().render(self)

    @classmethod
    def bulk_render(cls, actionId=None, viewId=None, **kwargs):
        action = cls.registry.Web.Action.query().get(int(actionId))
        view = cls.registry.get('Model.Web.View.' + viewId.split('-')[0])()
        return view.bulk_render(action, viewId)


@register(Mixin)  # noqa
class View:
    mode_name = None

    def render(self, view):
        buttons = [{'label': b.label, 'buttonId': b.method}
                   for b in view.action.buttons + view.buttons
                   if b.mode == 'action']
        buttons2 = [{'label': b.label, 'buttonId': b.method}
                    for b in view.action.buttons + view.buttons
                    if b.mode == 'more']
        return {
            'type': 'UPDATE_VIEW',
            'viewId': str(view.id),
            'viewType': self.mode_name,
            'creatable': view.action.add_new and view.add_new or False,
            'deletable': view.action.add_delete and view.add_delete or False,
            'editable': view.action.add_edit and view.add_edit or False,
            'model': view.action.model,
            'buttons': buttons,
            'onSelect_buttons': buttons2,
        }

    def bulk_render(self, action, viewId):
        buttons = [{'label': b.label, 'buttonId': b.method}
                   for b in action.buttons
                   if b.mode == 'action']
        buttons2 = [{'label': b.label, 'buttonId': b.method}
                    for b in action.buttons
                    if b.mode == 'more']
        return {
            'type': 'UPDATE_VIEW',
            'viewId': viewId,
            'viewType': self.mode_name,
            'creatable': action.add_new or False,
            'deletable': action.add_delete or False,
            'editable': action.add_edit or False,
            'model': action.model,
            'buttons': buttons,
            'onSelect_buttons': buttons2,
        }


@register(Mixin.View)  # noqa
class Template:

    def get_field_for_(self, field, _type, description):
        field.tag = 'furet-ui-%s-field-%s' % (
            self.mode_name.lower(), _type.lower())
        for attrib in description:
            if attrib in ('id', 'model', 'type', 'primary_key'):
                continue

            if attrib in field.attrib:
                continue

            if attrib == 'nullable':
                field.set('required', '1' if description[attrib] else '0')
            else:
                field.set(attrib, description[attrib])

    def get_field_for_Integer(self, field, description):
        return self.get_field_for_(field, 'Integer', description)

    def get_field_for_SmallInteger(self, field, description):
        return self.get_field_for_(field, 'Integer', description)

    def get_field_for_File(self, field, description):
        return self.get_field_for_(field, 'File', description)

    def get_field_for_Sequence(self, field, description):
        description['readonly'] = True
        return self.get_field_for_(field, 'String', description)

    def get_field_for_Selection(self, field, description):
        selections = {}
        if 'selections' in description:
            selections = description['selections']
            del description['selections']

        if isinstance(selections, list):
            selections = dict(selections)

        description['{%s}selections' % field.nsmap['v-bind']] = str(selections)
        return self.get_field_for_(field, 'Selection', description)

    def get_field_for_UUID(self, field, description):
        description['readonly'] = True
        return self.get_field_for_(field, 'String', description)

    def replace_buttons(self, template, fields_description):
        buttons = template.findall('.//button')
        for el in buttons:
            el.tag = 'furet-ui-%s-button' % (self.mode_name.lower())
            self.add_template_bind(el)
            el.set('{%s}viewId' % el.nsmap['v-bind'], 'viewId')
            el.set('{%s}model' % el.nsmap['v-bind'], 'model')
            el.set('{%s}options' % el.nsmap['v-bind'],
                   el.attrib.get('data-options', '{}'))
            el.set('buttonId', el.attrib.get('data-method', ''))

    def replace_fields(self, template, fields_description):
        fields = template.findall('.//field')
        for el in fields:
            fd = fields_description[el.attrib.get('name')]
            _type = el.attrib.get('type', fd['type'])
            if _type == 'FakeColumn':
                continue

            meth = 'get_field_for_' + _type
            if hasattr(self, meth):
                getattr(self, meth)(el, fd)
            else:
                self.get_field_for_(el, _type, fd)

            self.add_template_bind(el)

    def update_interface_attributes(self, template, fields_description):
        for el in template.findall('.//*[@visible-only-if]'):
            if el.tag == 'div':
                el.tag = 'furet-ui-%s-group' % (self.mode_name.lower())
                self.add_template_bind(el)

            el.set('invisible', '!(' + el.attrib['visible-only-if'] + ')')
            del el.attrib['visible-only-if']

        #TODO writable-only-if  warning propagation in children
        #TODO not-nullable-only-if  warning propagation in children

    def _encode_to_furetui(self, template, fields_description):
        nsmap = {'v-bind': 'https://vuejs.org/'}
        etree.cleanup_namespaces(template, top_nsmap=nsmap, keep_ns_prefixes=['v-bind'])
        self.update_interface_attributes(template, fields_description)
        self.replace_fields(template, fields_description)
        self.replace_buttons(template, fields_description)

    def encode_to_furetui(self, template, Model, fields):
        fields_description = Model.fields_description(fields)
        self._encode_to_furetui(template, fields_description)
        return self.registry.furetui_views.decode(
            html.tostring(template).decode('utf-8'))


@register(Mixin.View)  # noqa
class Multi:

    def get_form_view(self, view):
        views = [v.id
                 for v in view.action.views
                 if v.id != view.id and v.mode == 'Model.Web.View.Form']
        if views:
            return views[0]

        return None


@register(Model.Web.View)
class List(Mixin.View, Mixin.View.Multi):
    "List View"

    mode_name = 'List'

    def field_for_(self, field):
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

    def field_for_BigInteger(self, field):
        f = field.copy()
        f['type'] = 'Integer'
        return self.field_for_(f)

    def field_for_SmallInteger(self, field):
        f = field.copy()
        f['type'] = 'Integer'
        return self.field_for_(f)

    def field_for_LargeBinary(self, field):
        f = field.copy()
        f['type'] = 'file'
        return self.field_for_(f)

    def field_for_Sequence(self, field):
        f = field.copy()
        f['type'] = 'string'
        res = self.field_for_(f)
        res['readonly'] = True
        return res

    def field_for_Selection(self, field):
        f = field.copy()
        if isinstance(f['selections'], list):
            f['selections'] = dict(f['selections'])

        return self.field_for_(f)

    def field_for_UUID(self, field):
        f = field.copy()
        f['type'] = 'string'
        res = self.field_for_(f)
        res['readonly'] = True
        return res

    def bulk_render(self, action, viewType):
        res = super(List, self).bulk_render(action, viewType)
        Model = self.registry.get(action.model)
        Column = self.registry.System.Column
        query = Column.query().filter(Column.model == action.model)
        fields = query.order_by(Column.name).all().name
        headers = []
        search = []
        fd = Model.fields_description(fields)
        for field_name in fields:
            field = fd[field_name]
            if field['type'] == 'FakeColumn':
                continue

            meth = 'field_for_' + field['type']
            if hasattr(self, meth):
                headers.append(getattr(self, meth)(field))
            else:
                headers.append(self.field_for_(field))

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
class Thumbnail(Mixin.View, Mixin.View.Multi, Mixin.View.Template):
    "Thumbnail View"

    mode_name = 'Thumbnail'

    def add_template_bind(self, field):
        field.attrib['{%s}data' % field.nsmap['v-bind']] = "card"

    def render(self, view):
        res = super(Thumbnail, self).render(view)
        Model = self.registry.get(view.action.model)
        template = self.registry.furetui_views.get_template(
            view.template, tostring=False)
        template.tag = 'div'
        fields = [el.attrib.get('name') for el in template.findall('.//field')]
        search = []
        res.update({
            'onSelect': self.get_form_view(view),
            'template': self.encode_to_furetui(template, Model, fields),
            'border_fieldcolor': view.border_fieldcolor,
            'background_fieldcolor': view.background_fieldcolor,
            'search': search,
            'fields': fields,
        })
        return res


@register(Model.Web.View)
class Form(Mixin.View, Mixin.View.Template):
    "Form View"

    mode_name = 'Form'

    def add_template_bind(self, field):
        field.attrib['{%s}config' % field.nsmap['v-bind']] = "config"

    def render(self, view):
        res = super(Form, self).render(view)
        Model = self.registry.get(view.action.model)
        template = self.registry.furetui_views.get_template(
            view.template, tostring=False)
        template.tag = 'div'
        fields = [el.attrib.get('name') for el in template.findall('.//field')]
        res.update({
            'template': self.encode_to_furetui(template, Model, fields),
            'fields': fields,
        })
        return res

    def bulk_render(self, action, viewType):
        res = super(Form, self).bulk_render(action, viewType)
        Model = self.registry.get(action.model)
        fields = self.registry.System.Column.query().filter_by(
            model=action.model).all().name
        root = etree.Element("div")
        root.set('class', "columns is-multiline is-mobile")
        for field_name in fields:
            column = etree.SubElement(root, "div")
            column.set('class', "column is-4-desktop is-6-tablet is-12-mobile")
            field = etree.SubElement(column, "field")
            field.set('name', field_name)

        res.update({
            'onClose': 'List-%d' % action.id,
            'template': self.encode_to_furetui(root, Model, fields),
            'buttons': [],
            'fields': fields,
        })
        return res
