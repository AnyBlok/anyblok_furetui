# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#    Copyright (C) 2020 Pierre Verkest <pierreverkest84@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import json
from copy import deepcopy
from lxml import etree, html
from anyblok_furetui import ResourceTemplateRendererException
from anyblok.declarations import Declarations
from anyblok.column import Integer, String, Boolean, Selection, Json
from anyblok.relationship import Many2One
from anyblok_pyramid_rest_api.validator import FILTER_OPERATORS


@Declarations.register(Declarations.Mixin)  # noqa
class Template:

    def get_field_for_(self, field, _type, description, fields2read):

        required = field.attrib.get(
            'required', '1' if not description.get('nullable') else '0')
        if required == '':
            required = '1'

        config = {
            'name': field.attrib.get('name'),
            'type': _type.lower(),
            'label': field.attrib.get('label', description['label']),
            'tooltip': field.attrib.get('tooltip'),
            'model': field.attrib.get('model', description.get('model')),
            'required': required,
        }

        for key in ('readonly', 'writable', 'hidden'):
            value = description.get(key, field.attrib.get(key, '0'))
            if value == '':
                value = '1'
            elif key == value:
                value = '1'

            config[key] = value

        field.tag = 'furet-ui-field'
        attribs = list(description.keys())
        attribs.sort()
        fields2read.append(description['id'])
        for attrib in attribs:
            if attrib in ('id', 'label', 'type', 'primary_key',
                          'nullable', 'model'):
                continue
            else:
                config[attrib] = description[attrib]

        self.clean_unnecessary_attributes(field)
        field.attrib['{%s}config' % field.nsmap['v-bind']] = json.dumps(config)

    def get_field_for_String(self, field, description, fields2read):
        Model = self.registry.get(self.model)
        description.update({
            'maxlength': Model.registry.loaded_namespaces_first_step[
                self.model][description['id']].size,
            'placeholder': field.attrib.get('placeholder', ''),
            'icon': field.attrib.get('icon', ''),
        })
        return self.get_field_for_(field, 'String', description, fields2read)

    def get_field_for_Sequence(self, field, description, fields2read):
        description.update(dict(readonly='1'))
        return self.get_field_for_String(field, description, fields2read)

    def get_field_for_Password(self, field, description, fields2read):
        Model = self.registry.get(self.model)
        description.update({
            'maxlength': Model.registry.loaded_namespaces_first_step[
                self.model][description['id']].size,
            'placeholder': field.attrib.get('placeholder', ''),
            'icon': field.attrib.get('icon', ''),
        })
        for key in ('reveal',):
            value = field.attrib.get(key, '0')
            if value == '':
                value = '1'
            elif key == value:
                value = '1'

            description[key] = value
        return self.get_field_for_(field, 'Password', description, fields2read)

    def get_field_for_BarCode(self, field, description, fields2read):
        description.update({
            'placeholder': field.attrib.get('placeholder', ''),
            'icon': field.attrib.get('icon', ''),
        })
        options = description['options'] = {}
        for key in field.attrib:
            if key.startswith('barcode-'):
                options[key[8:]] = field.attrib[key]

        return self.get_field_for_(field, 'BarCode', description, fields2read)

    def get_field_for_Integer(self, field, description, fields2read):
        description.update({
            'min': field.attrib.get('min'),
            'max': field.attrib.get('max'),
        })
        return self.get_field_for_(field, 'Integer', description, fields2read)

    def get_field_for_BigInteger(self, field, description, fields2read):
        return self.get_field_for_Integer(field, description, fields2read)

    def get_field_for_Many2One(  # noqa: C901
        self, field, description, fields2read, relation="Many2One"
    ):
        Model = self.registry.get(description['model'])
        description = description.copy()
        display = field.attrib.get('display')
        if display:
            for op in ('!=', '==', '<', '<=', '>', '>='):
                display = display.replace(op, ' ')

            display = display.replace('!', '')
            fields = []
            for d in display.split():
                if 'fields.' in d:
                    fields.append(d.split('.')[1])

        else:
            fields = Model.get_display_fields()
            display = " + ', ' + ".join(['fields.' + x for x in fields])

        fields = list(set(fields))
        description['display'] = display

        filter_by = field.attrib.get('filter_by')
        if filter_by:
            filter_by = filter_by.split(',')
        else:
            filter_by = Model.get_filter_fields()

        resource = field.attrib.get('resource')
        menu = field.attrib.get('menu')
        if eval(field.attrib.get('no-link', 'False') or 'True'):
            pass
        elif menu:
            menu = self.registry.IO.Mapping.get(
                'Model.FuretUI.Menu.Resource', menu)
            resource = menu.resource
        elif resource:
            for type_ in ('set', 'form'):
                resource_model = 'Model.FuretUI.Resource.%s' % type_
                resource = self.registry.IO.Mapping.get(
                    resource_model, resource)
                if resource:
                    break
        else:
            query = self.registry.FuretUI.Resource.Form.query()
            query = query.filter_by(model=description['model'])
            resource = query.one_or_none()

        description['resource'] = resource.id if resource else None
        description['menu'] = menu.id if menu else None
        description['fields'] = fields
        description['filter_by'] = filter_by
        description['limit'] = field.attrib.get('limit', 10)
        fields2read.extend(['%s.%s' % (description['id'], x) for x in fields])
        return self.get_field_for_(field, relation, description, [])

    def get_field_for_x2Many(self, field, relation, description, fields2read):
        description = description.copy()
        model = description['model']
        resource = field.attrib.get('resource-external_id')
        if not resource:
            query = self.registry.FuretUI.Resource.List.query()
            query = query.filter_by(model=model)
            resource = query.one_or_none()
        else:
            resource_type = field.attrib.get('resource-type', 'set')
            resource_model = 'Model.FuretUI.Resource.%s' % (
                resource_type.capitalize())
            resource = self.registry.IO.Mapping.get(resource_model, resource)
            if not resource:
                for type_ in ('set', 'list', 'thumbnail'):
                    resource_model = 'Model.FuretUI.Resource.%s' % type_
                    resource = self.registry.IO.Mapping.get(
                        resource_model, resource)
                    if resource:
                        break

        if resource:
            description['resource'] = resource.id

        fields = self.registry.get(model).get_primary_keys()
        fields2read.extend(['%s.%s' % (description['id'], x) for x in fields])
        return self.get_field_for_(field, relation, description, [])

    def get_field_for_One2Many(self, field, description, fields2read):
        return self.get_field_for_x2Many(field, 'One2Many', description, [])

    def get_field_for_Many2ManyTags(self, field, description, fields2read):
        return self.get_field_for_Many2One(
            field, description, fields2read, relation="Many2ManyTags")

    def get_field_for_Many2Many(self, field, description, fields2read):
        return self.get_field_for_x2Many(field, 'Many2Many', description, [])

    def get_field_for_DateTime(self, field, description, fields2read):
        description.update({
            'placeholder': field.attrib.get('placeholder', ''),
            'editable': eval(field.attrib.get('editable', 'True')),
            'icon': field.attrib.get('icon', ''),
            'datepicker': {
              'showWeekNumber': eval(
                  field.attrib.get('show-week-number', 'True')),
            },
            'timepicker': {
                'enableSeconds': eval(field.attrib.get('show-second', 'True')),
                'hourFormat': field.attrib.get('hour-format', '24'),
            },
        })
        return self.get_field_for_(field, 'DateTime', description, fields2read)

    def get_field_for_TimeStamp(self, field, description, fields2read):
        self.get_field_for_DateTime(field, description, fields2read)

    def get_field_for_Selection(self, field, description, fields2read):
        description = deepcopy(description)
        for key in ('selections', 'colors'):
            if key in field.attrib:
                description[key] = eval(field.attrib.get(key), {}, {})

            if key not in description:
                description[key] = {}

            if isinstance(description[key], list):
                description[key] = dict(description[key])

        return self.get_field_for_(field, 'Selection', description, fields2read)

    def get_field_for_StatusBar(self, field, description, fields2read):
        description = deepcopy(description)
        for key in ('selections',):
            if key in field.attrib:
                description[key] = eval(field.attrib.get(key), {}, {})

            if key not in description:
                description[key] = {}

            if isinstance(description[key], list):
                description[key] = dict(description[key])

        for key in ('done-states', 'dangerous-states'):
            description[key] = [
                x.strip() for x in field.attrib.get(key, '').split(',')]

        return self.get_field_for_(field, 'StatusBar', description, fields2read)

    def replace_buttons(self, userid, template, fields_description,
                        fields2read):
        buttons = template.findall('.//button')
        for el in buttons:
            el.tag = 'furet-ui-form-button'
            config = {
                'label': el.attrib['label'],
                'class': el.attrib.get('class', '').split(),
            }
            if 'call' in el.attrib:
                call = el.attrib['call']
                if call not in self.registry.exposed_methods.get(self.model,
                                                                 {}):
                    raise ResourceTemplateRendererException(
                        f"On resource {self.identity} : The button "
                        f"{config} define an unexposed method '{call}'"
                    )

                definition = self.registry.exposed_methods[self.model][call]
                permission = definition['permission']
                if permission is not None:
                    if not self.registry.Pyramid.check_acl(
                        userid, self.model, permission
                    ):
                        el.getparent().remove(el)
                        return

                config['call'] = call
            elif 'open-resource' in el.attrib:
                resource = None
                for model in self.__class__.get_resource_types().keys():
                    resource = self.registry.IO.Mapping.get(
                        model, el.attrib['open-resource'])
                    if resource:
                        break

                if resource is None:
                    raise ResourceTemplateRendererException(
                        f"On resource {self.identity} : The button "
                        f"{config} defined an unmapped resource "
                        f"{el.attrib['open-resource']}")

                config['open_resource'] = el.attrib['open-resource']
            else:
                raise ResourceTemplateRendererException(
                    f"On resource {self.identity} : The button "
                    f"{config} doesn't define call or resource")

            config.update(self.update_interface_attributes(
                el, fields2read, 'readonly', 'hidden'))
            config.pop('props', None)

            self.clean_unnecessary_attributes(el)
            el.attrib['{%s}config' % el.nsmap['v-bind']] = json.dumps(config)
            self.add_template_bind(el)

    def clean_unnecessary_attributes(self, el, *allows):
        for key in el.attrib:
            if key not in allows:
                del el.attrib[key]

    def replace_fields(self, template, fields_description, fields2read):
        fields = template.findall('.//field')
        for el in fields:
            fd = deepcopy(fields_description[el.attrib.get('name')])
            _type = el.attrib.get('widget', fd['type'])
            if _type == 'FakeColumn':
                continue

            meth = 'get_field_for_' + _type
            if hasattr(self, meth):
                getattr(self, meth)(el, fd, fields2read)
            else:
                self.get_field_for_(el, _type, fd, fields2read)

            self.add_template_bind(el)

    def update_interface_attributes(self, el, fields2read, *attributes):
        config = {}
        for key in attributes:
            value = el.attrib.get(key)
            if value == '':
                value = '1'
            elif value == key:
                value = '1'

            if not value:
                continue

            fields = value
            for op in ('!=', '==', '<', '<=', '>', '>='):
                fields = fields.replace(op, ' ')

            fields = fields.replace('!', '')
            fields = [d.strip().split('.')[1]
                      for d in fields.split(' ')
                      if 'fields.' in d]

            config[key] = value
            fields2read.extend(fields)

        if config:
            config['props'] = initial_props = {}
            for key in el.attrib:
                if key in attributes:
                    continue

                initial_props[key] = el.attrib.get(key)

        return config

    def replace_divs(self, template, fields2read):
        fields = template.findall('.//div')
        for el in fields:
            config = self.update_interface_attributes(
                el, fields2read, 'hidden')
            if not config:
                continue

            el.tag = 'furet-ui-div'
            self.clean_unnecessary_attributes(el, 'class')
            self.add_template_bind(el)
            el.attrib['{%s}config' % el.nsmap['v-bind']] = str(config)

    def replace_by_(self, template, fields2read, tag):
        tags = template.findall('.//%s' % tag)
        for el in tags:
            config = self.update_interface_attributes(
                el, fields2read, 'readonly', 'hidden', 'writable')

            el.tag = 'furet-ui-%s' % tag
            self.clean_unnecessary_attributes(el, 'class', 'label')
            self.add_template_bind(el)
            el.attrib['{%s}config' % el.nsmap['v-bind']] = str(config)

    def replace_fieldsets(self, template, fields2read):
        self.replace_by_(template, fields2read, 'fieldset')

    def replace_selector(self, template, fields2read):
        tags = template.findall('.//selector')
        count = 0
        for el in tags:
            config = self.update_interface_attributes(
                el, fields2read, 'readonly', 'hidden')

            config['name'] = 'tag%d' % count
            count += 1

            for key in ('selections', 'selection_colors', 'name'):
                if key in el.attrib:
                    config[key] = el.attrib[key]

            if 'model' in el.attrib:
                Model = self.registry.get(el.attrib['model'])
                query = Model.query()
                code = el.attrib['field_code']
                label = el.attrib['field_label']
                config['selections'] = {getattr(x, code): getattr(x, label)
                                        for x in query}
            elif 'selections' not in el.attrib:
                raise ResourceTemplateRendererException(
                    f"On resource {self.id}, The  selector {config} does not "
                    f"declare model or selections"
                )

            el.tag = 'furet-ui-selector'
            self.clean_unnecessary_attributes(el, 'class')
            self.add_template_bind(el)
            el.attrib['{%s}config' % el.nsmap['v-bind']] = str(config)

    def replace_tabs(self, template, fields2read):
        tags = template.findall('.//tabs')
        counter = 0
        for el in tags:
            counter += 1
            config = self.update_interface_attributes(
                el, fields2read, 'readonly', 'hidden', 'writable')

            el.tag = 'furet-ui-tabs'
            config['name'] = el.attrib.get('name', f'tabs{counter}')
            self.clean_unnecessary_attributes(el, 'class')
            self.add_template_bind(el)
            el.attrib['{%s}config' % el.nsmap['v-bind']] = str(config)

    def replace_tab(self, template, fields2read):
        self.replace_by_(template, fields2read, 'tab')

    def _encode_to_furetui(self, userid, template, fields_description,
                           fields2read):
        nsmap = {'v-bind': 'https://vuejs.org/'}
        etree.cleanup_namespaces(
            template, top_nsmap=nsmap, keep_ns_prefixes=['v-bind'])
        self.replace_divs(template, fields2read)
        self.replace_selector(template, fields2read)
        self.replace_fieldsets(template, fields2read)
        self.replace_tabs(template, fields2read)
        self.replace_tab(template, fields2read)
        self.replace_fields(template, fields_description, fields2read)
        self.replace_buttons(userid, template, fields_description, fields2read)

    def encode_to_furetui(self, userid, template, fields, fields2read):
        Model = self.registry.get(self.model)
        fields_description = Model.fields_description(fields)
        self._encode_to_furetui(
            userid, template, fields_description, fields2read)
        return self.registry.furetui_templates.decode(
            html.tostring(template).decode('utf-8'))

    def add_template_bind(self, field):
        field.attrib['{%s}resource' % field.nsmap['v-bind']] = "resource"
        field.attrib['{%s}data' % field.nsmap['v-bind']] = "data"


@Declarations.register(Declarations.Model.FuretUI)
class Resource:

    id = Integer(primary_key=True)
    code = String()
    type = Selection(
        selections='get_resource_types',
        nullable=False)

    @classmethod
    def get_resource_types(cls):
        return {
            'Model.FuretUI.Resource.Custom': 'Custom',
            'Model.FuretUI.Resource.Set': 'Set',
            'Model.FuretUI.Resource.List': 'List',
            'Model.FuretUI.Resource.Thumbnail': 'Thumbnail',
            'Model.FuretUI.Resource.Form': 'Form',
            'Model.FuretUI.Resource.Dashboard': 'Dashboard',
        }

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Resource, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.FuretUI.Resource':
            mapper_args.update({'polymorphic_on': cls.type})
            mapper_args.update({'polymorphic_identity': None})
        else:
            mapper_args.update({'polymorphic_identity': cls.__registry_name__})

        return mapper_args

    @property
    def identity(self):
        Mapping = self.registry.IO.Mapping
        mapping = Mapping.get_from_model_and_primary_keys(
            self.__registry_name__, {'id': self.id})
        if mapping is not None:
            return mapping.key

        return self.id

    def get_definitions(self, **kwargs):
        raise Exception('This method must be over right')

    def to_dict(self, *a, **kw):
        res = super(Resource, self).to_dict(*a, **kw)
        if 'type' in res:
            res['type'] = self.type.label.lower()

        return res

    def check_acl(self, authenticated_userid):
        if not self.code:
            return True

        type_ = self.type.label.lower()
        return self.registry.FuretUI.check_acl(
            authenticated_userid, self.code, type_)

    def get_menus(self, authenticated_userid):
        return self.registry.FuretUI.Menu.get_menus_from(
            authenticated_userid, resource=self)


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Custom(Declarations.Model.FuretUI.Resource):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use('id'))
    component = String(nullable=False)

    def get_definitions(self, **kwargs):
        return [self.to_dict()]


@Declarations.register(Declarations.Model.FuretUI.Resource)
class List(Declarations.Model.FuretUI.Resource):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use(
                     'id').options(ondelete='cascade'))
    title = String()
    model = String(nullable=False, size=256,
                   foreign_key=Declarations.Model.System.Model.use(
                       'name').options(ondelete='cascade'))
    template = String()

    def field_for_(cls, field, fields2read, **kwargs):
        widget = kwargs.get('widget', field['type']).lower()
        res = {
            'hidden': False,
            'name': field['id'],
            'label': kwargs.get('label', field['label']),
            'component': kwargs.get('component', 'furet-ui-field'),
            'type': widget,
            'sticky': False,
            'numeric': (
                True if widget in ('integer', 'float', 'decimal') else False),
            'tooltip': kwargs.get('tooltip'),
        }
        for key in ('sortable', 'column-can-be-hidden', 'hidden-column',
                    'hidden', 'sticky'):
            if key in kwargs:
                value = kwargs[key]
                if value == '':
                    res[key] = True
                else:
                    res[key] = value

        fields2read.append(field['id'])
        for k in field:
            if k in ('id', 'label', 'nullable', 'primary_key', 'type'):
                continue
            elif k == 'model':
                if field[k]:
                    res[k] = field[k]
            else:
                res[k] = field[k]

        return res

    def field_for_BarCode(self, field, fields2read, **kwargs):
        f = field.copy()
        f['options'] = options = {}
        for key in kwargs:
            if key.startswith('barcode-'):
                options[key[8:]] = kwargs[key]

        return self.field_for_(f, fields2read, **kwargs)

    def field_for_Sequence(self, field, fields2read, **kwargs):
        f = field.copy()
        f['type'] = 'String'
        return self.field_for_(f, fields2read, **kwargs)

    def field_for_BigInteger(self, field, fields2read, **kwargs):
        f = field.copy()
        f['type'] = 'Integer'
        return self.field_for_(f, fields2read, **kwargs)

    def field_for_relationship(self, field, fields2read, **kwargs):
        f = field.copy()
        Model = self.registry.get(f['model'])
        # Mapping = cls.registry.IO.Mapping
        if 'display' in kwargs:
            display = kwargs['display']
            for op in ('!=', '==', '<', '<=', '>', '>='):
                display = display.replace(op, ' ')

            display = display.replace('!', '')
            fields = []
            for d in display.split():
                if 'fields.' in d:
                    fields.append(d.split('.')[1])

            f['display'] = kwargs['display']
            del kwargs['display']
        else:
            fields = Model.get_display_fields()
            f['display'] = " + ', ' + ".join(['fields.' + x for x in fields])

        resource = None
        menu = None
        if eval(kwargs.get('no-link', 'False') or 'True'):
            pass
        elif 'menu' in kwargs:
            menu = self.registry.IO.Mapping.get(
                'Model.FuretUI.Menu.Resource', kwargs['menu'])
            resource = menu.resource
        elif 'resource' in kwargs:
            for type_ in ('Set', 'Form'):
                resource_model = 'Model.FuretUI.Resource.%s' % type_
                resource = self.registry.IO.Mapping.get(
                    resource_model, kwargs['resource'])
                if resource:
                    break
        else:
            query = self.registry.FuretUI.Resource.Form.query()
            query = query.filter_by(model=f['model'])
            resource = query.one_or_none()

        f['resource'] = resource.id if resource else None
        f['menu'] = menu.id if menu else None
        fields2read.extend(['%s.%s' % (field['id'], x) for x in fields])
        return self.field_for_(f, [], **kwargs)

    def field_for_Many2One(self, field, fields2read, **kwargs):
        return self.field_for_relationship(field, fields2read, **kwargs)

    def field_for_One2One(self, field, fields2read, **kwargs):
        return self.field_for_relationship(field, fields2read, **kwargs)

    def field_for_Many2Many(self, field, fields2read, **kwargs):
        return self.field_for_relationship(field, fields2read, **kwargs)

    def field_for_One2Many(self, field, fields2read, **kwargs):
        return self.field_for_relationship(field, fields2read, **kwargs)

    def field_for_Selection(self, field, fields2read, **kwargs):
        f = field.copy()
        for key in ('selections', 'colors'):
            if key in kwargs:
                f[key] = eval(kwargs[key], {}, {})
                del kwargs[key]

            if key not in f:
                f[key] = {}

            if isinstance(f[key], list):
                f[key] = dict(f[key])

        return self.field_for_(f, fields2read, **kwargs)

    def field_for_StatusBar(self, field, fields2read, **kwargs):
        f = field.copy()
        for key in ('selections',):
            if key in kwargs:
                f[key] = eval(kwargs[key], {}, {})
                del kwargs[key]

            if key not in f:
                f[key] = {}

            if isinstance(f[key], list):
                f[key] = dict(f[key])

        for key in ('done-states', 'dangerous-states'):
            f[key] = [
                x.strip() for x in kwargs.get(key, '').split(',')]

        return self.field_for_(f, fields2read, **kwargs)

    def button_for(self, userid, Model, button, pks):
        attributes = deepcopy(button.attrib)
        if 'call' in attributes:
            call = attributes['call']
            model = Model.__registry_name__
            if call not in self.registry.exposed_methods.get(model, {}):
                raise ResourceTemplateRendererException(
                    f"On resource {self.identity} : The button "
                    f"{attributes} define an unexposed method '{call}'"
                )

            definition = self.registry.exposed_methods[model][call]
            permission = definition['permission']
            if permission is not None:
                if not self.registry.Pyramid.check_acl(
                    userid, model, permission
                ):
                    return None

        elif 'open-resource' in attributes:
            resource = None
            for model in self.__class__.get_resource_types().keys():
                resource = self.registry.IO.Mapping.get(
                    model, attributes['open-resource'])
                if resource:
                    break

            if resource is None:
                raise ResourceTemplateRendererException(
                    f"On resource {self.identity} : The button "
                    f"{attributes} defined an unmapped resource "
                    f"{button.attrib['open-resource']}")
        else:
            raise ResourceTemplateRendererException(
                f"On resource {self.identity} : The button "
                f"{attributes} doesn't define call or resource")

        attributes['pks'] = pks
        return attributes

    def get_definitions(self, **kwargs):
        Model = self.registry.get(self.model)
        fd = Model.fields_description()
        headers = []
        fields2read = []
        pks = Model.get_primary_keys()
        fields2read.extend(pks)
        buttons = []
        if self.template:
            template = self.registry.FuretUI.get_template(
                self.template, tostring=False)
            # FIXME button in header
            for field in template.findall('.//field'):
                attributes = deepcopy(field.attrib)
                field = fd[attributes.pop('name')]
                _type = attributes.get('widget', field['type'])
                meth = 'field_for_' + _type
                if hasattr(self.__class__, meth):
                    headers.append(getattr(self, meth)(
                        field, fields2read, **attributes))
                else:
                    headers.append(self.field_for_(
                        field, fields2read, **attributes))

            for button in template.findall('.//buttons/button'):
                attributes = self.button_for(
                    kwargs.get('authenticated_userid', None),
                    Model, button, pks)
                if attributes is not None:
                    buttons.append(attributes)

        else:
            fields = list(fd.keys())
            fields.sort()
            for field_name in fields:
                field = fd[field_name]
                if field['type'] in ('FakeColumn', 'Many2Many', 'One2Many',
                                     'Function'):
                    continue

                meth = 'field_for_' + field['type']
                if hasattr(self, meth):
                    headers.append(getattr(self, meth)(field, fields2read))
                else:
                    headers.append(self.field_for_(field, fields2read))

        fields2read = list(set(fields2read))
        fields2read.sort()

        res = [{
            'id': self.id,
            'type': self.type.label.lower(),
            'title': self.title,
            'model': self.model,
            'filters': self.registry.FuretUI.Resource.Filter.get_for_resource(
                list=self),
            'tags': self.registry.FuretUI.Resource.Tags.get_for_resource(
                list=self),
            'buttons': buttons,
            # 'on_selected_buttons': [],  # TODO
            'headers': headers,
            'fields': fields2read,
        }]
        return res


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Thumbnail(Declarations.Model.FuretUI.Resource):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use('id'))
    model = String(nullable=False, size=256,
                   foreign_key=Declarations.Model.System.Model.use('name'))
    template = String(nullable=False)
    # TODO criteria of filter


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Filter:
    id = Integer(primary_key=True)
    key = String(nullable=False)
    list = Many2One(model=Declarations.Model.FuretUI.Resource.List,
                    one2many="filters")
    thumbnail = Many2One(model=Declarations.Model.FuretUI.Resource.Thumbnail,
                         one2many="filters")
    mode = Selection(selections={'include': 'Include', 'exclude': 'Exclude'},
                     default='include', nullable=False)
    op = Selection(selections={x: x for x in FILTER_OPERATORS},
                   default='or-ilike', nullable=False)
    label = String(nullable=False)
    values = String()

    @classmethod
    def get_for_resource(cls, **resource):
        query = cls.query().filter_by(**resource)
        res = [{'values': x.values.split(',') if x.values else [],
                **x.to_dict('key', 'mode', 'op', 'label')}
               for x in query]
        return res


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Tags:
    id = Integer(primary_key=True)
    key = String(nullable=False)
    label = String(nullable=False)
    list = Many2One(model=Declarations.Model.FuretUI.Resource.List,
                    one2many="tags")
    thumbnail = Many2One(model=Declarations.Model.FuretUI.Resource.Thumbnail,
                         one2many="tags")

    @classmethod
    def get_for_resource(cls, **resource):
        query = cls.query().filter_by(**resource)
        return [x.to_dict('key', 'label') for x in query]


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Form(
    Declarations.Model.FuretUI.Resource,
    Declarations.Mixin.Template
):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use(
                    'id').options(ondelete='cascade'))
    model = String(foreign_key=Declarations.Model.System.Model.use(
                    'name').options(ondelete='cascade'),
                   nullable=False, size=256)
    template = String()
    polymorphic_columns = String()
    # TODO field Selection RO / RW / WO

    def get_classical_definitions(self, **kwargs):
        res = self.to_dict('id', 'type', 'model')
        userid = kwargs.get('authenticated_userid')
        Model = self.registry.get(self.model)
        fd = Model.fields_description()
        if self.template:
            template = self.registry.FuretUI.get_template(
                self.template, tostring=False)
            template.tag = 'div'
            fields = [el.attrib.get('name')
                      for el in template.findall('.//field')]
        else:
            fields = [x for x in fd.keys()
                      if fd[x]['type'] not in ('FakeColumn', 'Function')]
            fields.sort()
            template = etree.Element("div")
            template.set('class', "columns is-multiline is-mobile")
            for field_name in fields:
                column = etree.SubElement(template, "div")
                column.set('class',
                           "column is-4-desktop is-6-tablet is-12-mobile")
                field = etree.SubElement(column, "field")
                field.set('name', field_name)

        fields2read = []
        for tag in ('header', 'footer'):
            sub_template = template.find('./%s' % tag)
            if not sub_template:
                continue

            sub_template.tag = 'div'
            template.remove(sub_template)
            res['%s_template' % tag] = self.encode_to_furetui(
                userid, sub_template, fields, fields2read)

        body_template = self.encode_to_furetui(
            userid, template, fields, fields2read)
        fields2read = list(set(fields2read))
        fields2read.sort()
        res.update({
            'body_template': body_template,
            'fields': fields2read,
        })
        return [res]

    def get_polymorphic_definitions(self, **kwargs):
        res = []
        forms = []

        definition = self.to_dict('id', 'model')
        definition.update({
            'fields': self.polymorphic_columns.split(','),
            'type': 'polymorphicform',
            'forms': forms,
        })
        res.append(definition)
        for form in self.forms:
            forms.append({
                'waiting_value': form.polymorphic_values,
                'resource_id': form.resource.id,
            })
            res.extend(form.resource.get_definitions(**kwargs))

        return res

    def get_primary_keys_for(self):
        return self.registry.get(self.model).get_primary_keys()

    def get_definitions(self, **kwargs):
        if self.polymorphic_columns:
            if not self.polymorphic_columns:
                raise Exception(
                    'No polymorphic_columns defined for %r' % self)

            return self.get_polymorphic_definitions(**kwargs)

        return self.get_classical_definitions(**kwargs)


@Declarations.register(Declarations.Model.FuretUI.Resource)
class PolymorphicForm():
    id = Integer(primary_key=True)
    parent = Many2One(model=Declarations.Model.FuretUI.Resource.Form,
                      one2many="forms")
    polymorphic_values = Json(nullable=False)
    resource = Many2One(model=Declarations.Model.FuretUI.Resource.Form)


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Set(Declarations.Model.FuretUI.Resource):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use('id'))
    can_create = Boolean(default=True)
    can_read = Boolean(default=True)
    can_update = Boolean(default=True)
    can_delete = Boolean(default=True)

    acl_create = String()
    acl_read = String()
    acl_update = String()
    acl_delete = String()

    form = Many2One(model=Declarations.Model.FuretUI.Resource.Form,
                    nullable=False)
    multi_type = Selection(
        selections={'list': 'List', 'thumbnail': 'Thumbnail'},
        nullable=False, default="list")
    list = Many2One(model=Declarations.Model.FuretUI.Resource.List)
    thumbnail = Many2One(model=Declarations.Model.FuretUI.Resource.Thumbnail)
    # TODO add checkonstraint on multi + select

    def get_definitions(self, authenticated_userid=None, **kwargs):
        definition = self.to_dict('id', 'type')
        check_acl = self.registry.FuretUI.check_acl
        for acl in ('create', 'read', 'update', 'delete'):
            if getattr(self, 'can_%s' % acl):
                if not self.code:
                    definition['can_%s' % acl] = True
                else:
                    type_ = getattr(self, 'acl_%s' % acl)
                    definition['can_%s' % acl] = check_acl(
                        authenticated_userid, self.code, type_)
            else:
                definition['can_%s' % acl] = False

        definition.update({
            'pks': self.form.get_primary_keys_for(),
            'form': self.form.id,
            'multi': getattr(self, self.multi_type).id,
        })
        res = [definition]
        res.extend(self.form.get_definitions(
            authenticated_userid=authenticated_userid))
        res.extend(getattr(self, self.multi_type).get_definitions(
            authenticated_userid=authenticated_userid))
        return res

    def check_acl(self, authenticated_userid):
        multi = getattr(self, self.multi_type)
        return multi.check_acl(authenticated_userid)
