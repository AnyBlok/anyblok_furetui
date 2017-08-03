from anyblok import Declarations
from anyblok.column import Integer, Boolean, String, Selection
from anyblok.relationship import Many2One
from lxml import etree, html
from copy import deepcopy


register = Declarations.register
Model = Declarations.Model
Mixin = Declarations.Mixin


@register(Model.Web)
class View:
    mode_name = None

    id = Integer(primary_key=True)
    order = Integer(sequence='web__view_order_seq', nullable=False)
    action = Many2One(model=Model.Web.Action, one2many='views', nullable=False)
    mode = Selection(selections='get_mode_choices', nullable=False)
    template = String(nullable=False)
    add_delete = Boolean(default=True)
    add_new = Boolean(default=True)
    add_edit = Boolean(default=True)

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

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(View, cls).define_mapper_args()
        mapper_args.update({
            'polymorphic_identity': '',
            'polymorphic_on': cls.mode,
        })
        return mapper_args

    def render(self):
        buttons = [{'label': b.label, 'buttonId': b.method}
                   for b in self.action.buttons + self.buttons
                   if b.mode == 'action']
        return {
            'type': 'UPDATE_VIEW',
            'viewId': str(self.id),
            'viewType': self.mode_name,
            'creatable': self.action.add_new and self.add_new or False,
            'deletable': self.action.add_delete and self.add_delete or False,
            'editable': self.action.add_edit and self.add_edit or False,
            'model': self.action.model,
            'buttons': buttons,
        }

    @classmethod
    def bulk_render(cls, actionId=None, viewId=None, **kwargs):
        action = cls.registry.Web.Action.query().get(int(actionId))
        buttons = [{'label': b.label, 'buttonId': b.method}
                   for b in action.buttons
                   if b.mode == 'action']
        return {
            'type': 'UPDATE_VIEW',
            'viewId': viewId,
            'viewType': cls.mode_name,
            'creatable': action.add_new or False,
            'deletable': action.add_delete or False,
            'editable': action.add_edit or False,
            'model': action.model,
            'buttons': buttons,
        }


@register(Mixin)  # noqa
class Template:

    @classmethod
    def get_field_for_(cls, field, _type, description):
        field.tag = 'furet-ui-%s-field-%s' % (
            cls.mode_name.lower(), _type.lower())
        attribs = list(description.keys())
        attribs.sort()
        for attrib in attribs:
            if attrib in ('id', 'model', 'type', 'primary_key'):
                continue

            if attrib in field.attrib:
                continue

            if attrib == 'nullable':
                field.set('required', '1' if description[attrib] else '0')
            else:
                field.set(attrib, description[attrib])

    @classmethod
    def get_field_for_Integer(cls, field, description):
        return cls.get_field_for_(field, 'Integer', description)

    @classmethod
    def get_field_for_SmallInteger(cls, field, description):
        return cls.get_field_for_(field, 'Integer', description)

    @classmethod
    def get_field_for_File(cls, field, description):
        return cls.get_field_for_(field, 'File', description)

    @classmethod
    def get_field_for_Sequence(cls, field, description):
        description['readonly'] = True
        return cls.get_field_for_(field, 'String', description)

    @classmethod
    def get_field_for_Selection(cls, field, description):
        selections = {}
        if 'selections' in description:
            selections = description['selections']
            del description['selections']

        if isinstance(selections, list):
            selections = dict(selections)

        description['{%s}selections' % field.nsmap['v-bind']] = str(selections)
        return cls.get_field_for_(field, 'Selection', description)

    @classmethod
    def get_field_for_UUID(cls, field, description):
        description['readonly'] = True
        return cls.get_field_for_(field, 'String', description)

    @classmethod
    def replace_buttons(cls, template, fields_description):
        buttons = template.findall('.//button')
        for el in buttons:
            el.tag = 'furet-ui-%s-button' % (cls.mode_name.lower())
            cls.add_template_bind(el)
            el.set('{%s}viewId' % el.nsmap['v-bind'], 'viewId')
            el.set('{%s}model' % el.nsmap['v-bind'], 'model')
            el.set('{%s}options' % el.nsmap['v-bind'],
                   el.attrib.get('data-options', '{}'))
            el.set('buttonId', el.attrib.get('data-method', ''))

    @classmethod
    def replace_fields(cls, template, fields_description):
        fields = template.findall('.//field')
        for el in fields:
            fd = deepcopy(fields_description[el.attrib.get('name')])
            _type = el.attrib.get('type', fd['type'])
            if _type == 'FakeColumn':
                continue

            meth = 'get_field_for_' + _type
            if hasattr(cls, meth):
                getattr(cls, meth)(el, fd)
            else:
                cls.get_field_for_(el, _type, fd)

            cls.add_template_bind(el)

    @classmethod
    def update_interface_attributes(cls, template, fields_description):
        for el in template.findall('.//*[@visible-only-if]'):
            if el.tag == 'div':
                el.tag = 'furet-ui-%s-group' % (cls.mode_name.lower())
                cls.add_template_bind(el)

            el.set('invisible', '!(' + el.attrib['visible-only-if'] + ')')
            del el.attrib['visible-only-if']

        #TODO writable-only-if  warning propagation in children
        #TODO not-nullable-only-if  warning propagation in children

    @classmethod
    def _encode_to_furetui(cls, template, fields_description):
        nsmap = {'v-bind': 'https://vuejs.org/'}
        etree.cleanup_namespaces(template, top_nsmap=nsmap, keep_ns_prefixes=['v-bind'])
        cls.update_interface_attributes(template, fields_description)
        cls.replace_fields(template, fields_description)
        cls.replace_buttons(template, fields_description)

    @classmethod
    def encode_to_furetui(cls, template, Model, fields):
        fields_description = Model.fields_description(fields)
        cls._encode_to_furetui(template, fields_description)
        return cls.registry.furetui_views.decode(
            html.tostring(template).decode('utf-8'))


@register(Mixin)  # noqa
class Multi:

    def get_form_view(self):
        views = [v.id
                 for v in self.action.views
                 if v.id != self.id and v.mode == 'Model.Web.View.Form']
        if views:
            return views[0]

        return None


@register(Model.Web.View)
class List(Model.Web.View, Mixin.Multi):
    "List View"

    mode_name = 'List'

    id = Integer(
        primary_key=True,
        foreign_key=Model.Web.View.use('id').options(ondelete="CASCADE")
    )
    selectable = Boolean(default=False)

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(List, cls).define_mapper_args()
        mapper_args.update({
            'polymorphic_identity': 'Model.Web.View.List',
        })
        return mapper_args

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
        if 'selections' not in f:
            f['selections'] = {}

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
    def bulk_render(cls, actionId=None, viewId=None, **kwargs):
        action = cls.registry.Web.Action.query().get(int(actionId))
        res = super(List, cls).bulk_render(
            actionId=actionId, viewId=viewId, **kwargs)
        Model = cls.registry.get(action.model)
        headers = []
        search = []
        fd = Model.fields_description()
        fields = list(fd.keys())
        fields.sort()
        toRemoveFields = []
        for field_name in fields:
            field = fd[field_name]
            if field['type'] in ('FakeColumn', 'Many2Many', 'One2Many',
                                 'Function'):
                toRemoveFields.append(field_name)
                continue

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

        buttons2 = [{'label': b.label, 'buttonId': b.method}
                    for b in action.buttons
                    if b.mode == 'more']
        res.update({
            'selectable': False,
            'onSelect': 'Form-%d' % action.id,
            'headers': headers,
            'search': search,
            'buttons': [],
            'onSelect_buttons': buttons2,
            'fields': [f for f in fields if f not in toRemoveFields],
        })
        return res


@register(Model.Web.View)
class Thumbnail(Model.Web.View, Mixin.Multi, Mixin.Template):
    "Thumbnail View"

    mode_name = 'Thumbnail'

    id = Integer(
        primary_key=True,
        foreign_key=Model.Web.View.use('id').options(ondelete="CASCADE")
    )
    # on_change = Many2One(model='Model.Web.View')
    border_fieldcolor = String(size=256)
    background_fieldcolor = String(size=256)

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Thumbnail, cls).define_mapper_args()
        mapper_args.update({
            'polymorphic_identity': 'Model.Web.View.Thumbnail',
        })
        return mapper_args

    @classmethod
    def add_template_bind(cls, field):
        field.attrib['{%s}data' % field.nsmap['v-bind']] = "card"

    def render(self):
        res = super(Thumbnail, self).render()
        Model = self.registry.get(self.action.model)
        template = self.registry.furetui_views.get_template(
            self.template, tostring=False)
        template.tag = 'div'
        fields = [el.attrib.get('name') for el in template.findall('.//field')]
        search = []
        res.update({
            'onSelect': self.get_form_view(),
            'template': self.encode_to_furetui(template, Model, fields),
            'border_fieldcolor': self.border_fieldcolor,
            'background_fieldcolor': self.background_fieldcolor,
            'search': search,
            'fields': fields,
        })
        return res


@register(Model.Web.View)
class Form(Model.Web.View, Mixin.Template):
    "Form View"

    mode_name = 'Form'

    id = Integer(
        primary_key=True,
        foreign_key=Model.Web.View.use('id').options(ondelete="CASCADE")
    )

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Form, cls).define_mapper_args()
        mapper_args.update({
            'polymorphic_identity': 'Model.Web.View.Form',
        })
        return mapper_args

    @classmethod
    def add_template_bind(cls, field):
        field.attrib['{%s}config' % field.nsmap['v-bind']] = "config"

    def render(self):
        res = super(Form, self).render()
        Model = self.registry.get(self.action.model)
        template = self.registry.furetui_views.get_template(
            self.template, tostring=False)
        template.tag = 'div'
        fields = [el.attrib.get('name') for el in template.findall('.//field')]
        res.update({
            'template': self.encode_to_furetui(template, Model, fields),
            'fields': fields,
        })
        return res

    @classmethod
    def bulk_render(cls, actionId=None, viewId=None, **kwargs):
        action = cls.registry.Web.Action.query().get(int(actionId))
        res = super(Form, cls).bulk_render(
            actionId=actionId, viewId=viewId, **kwargs)
        Model = cls.registry.get(action.model)
        fd = Model.fields_description()
        fields = [x for x in fd.keys()
                  if fd[x]['type'] not in ('FakeColumn', 'Function')]
        fields.sort()
        root = etree.Element("div")
        root.set('class', "columns is-multiline is-mobile")
        for field_name in fields:
            column = etree.SubElement(root, "div")
            column.set('class', "column is-4-desktop is-6-tablet is-12-mobile")
            field = etree.SubElement(column, "field")
            field.set('name', field_name)

        res.update({
            'onClose': 'List-%d' % action.id,
            'template': cls.encode_to_furetui(root, Model, fields),
            'buttons': [],
            'fields': fields,
        })
        return res
