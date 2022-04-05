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
from .translate import Translation
import re


pycountry = None
try:
    import pycountry
    if not pycountry.countries._is_loaded:
        pycountry.countries._load()

except ImportError:
    pass


def get_fields_from_string(string, prefix='fields'):
    return [x.split('.')[1]  # noqa: W605
            for x in re.findall("%s\.\w*" % prefix, string)]  # noqa W605


@Declarations.register(Declarations.Mixin)  # noqa
class Template:

    def extract_slot(self, field, attributes, fields2read):
        if not (bool(field.getchildren()) or bool(field.text)):
            return

        slot = deepcopy(field)
        slot.tag = 'div'
        for x in slot.attrib.keys():
            del slot.attrib[x]

        slot_str = etree.tostring(slot).decode('utf-8')
        fields = get_fields_from_string(slot_str)
        if fields:
            fields2read.extend(fields)
            for f in fields:
                slot_str = slot_str.replace('fields.%s' % f, 'data.%s' % f)

        attributes['slot'] = slot_str
        attributes['slot_fields'] = list(set(
            get_fields_from_string(slot_str, prefix='relation')))
        children = field.getchildren()
        for child in children:
            field.remove(child)

        field.text = ''

    def get_field_for_(self, field, _type, description, fields2read):

        required = field.attrib.get(
            'required', '1' if not description.get('nullable') else '0')
        if required == '':
            required = '1'

        config = {
            'name': field.attrib.get('name'),
            'type': _type.lower(),
            'label': field.attrib.get(
                'label',
                self.get_translated_label_for(
                    description['id'], description['label'])
             ),
            'tooltip': field.attrib.get('tooltip'),
            'model': field.attrib.get('model', description.get('model')),
            'required': required,
        }

        if description.get('slot'):
            config['slot'] = description['slot']

        for key in ('readonly', 'writable', 'hidden'):
            value = description.get(key, field.attrib.get(key, '0'))
            if value == '':
                value = '1'
            elif key == value:
                value = '1'

            config[key] = value
            fields2read.extend(get_fields_from_string(value))

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
        Model = self.anyblok.get(self.model)
        description.update({
            'maxlength': Model.anyblok.loaded_namespaces_first_step[
                self.model][description['id']].size,
            'placeholder': field.attrib.get('placeholder', ''),
            'icon': field.attrib.get('icon', ''),
        })
        return self.get_field_for_(field, 'String', description, fields2read)

    def get_field_for_PhoneNumber(self, field, description, fields2read):
        return self.get_field_for_(field, 'String', description, fields2read)

    def get_field_for_Sequence(self, field, description, fields2read):
        description.update(dict(readonly='1'))
        return self.get_field_for_String(field, description, fields2read)

    def get_field_for_Password(self, field, description, fields2read):
        Model = self.anyblok.get(self.model)
        description.update({
            'maxlength': Model.anyblok.loaded_namespaces_first_step[
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
        Model = self.anyblok.get(description['model'])
        description = description.copy()
        display = field.attrib.get('display')
        fields = []
        if description.get('slot'):
            fields.extend(description.pop('slot_fields'))

        if display:
            fields.extend(get_fields_from_string(display))
        else:
            fields.extend(Model.get_display_fields())
            display = " + ', ' + ".join(['fields.' + x for x in fields])

        fields = list(set(fields))
        fields.sort()
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
            menu = self.anyblok.IO.Mapping.get(
                'Model.FuretUI.Menu.Resource', menu)
            resource = menu.resource
        elif resource:
            for type_ in ('set', 'form'):
                resource_model = 'Model.FuretUI.Resource.%s' % type_
                resource = self.anyblok.IO.Mapping.get(
                    resource_model, resource)
                if resource:
                    break
        else:
            query = self.anyblok.FuretUI.Resource.Form.query()
            query = query.filter_by(model=description['model'])
            resource = query.one_or_none()

        description['resource'] = resource.id if resource else None
        description['menu'] = menu.id if menu else None
        description['fields'] = fields
        description['filter_by'] = filter_by
        description['tags'] = field.attrib.get('tags', '')
        description['limit'] = field.attrib.get('limit', 10)
        description['colors'] = field.attrib.get('color', '')

        if 'max-height' in field.attrib:
            description['maxheight'] = field.attrib.get('max-height')

        fields2read.extend(['%s.%s' % (description['id'], x) for x in fields])
        return self.get_field_for_(field, relation, description, [])

    def get_field_for_x2Many(self, field, relation, description, fields2read):
        description = description.copy()
        model = description['model']
        resource = field.attrib.get('resource-external_id')
        if not resource:
            query = self.anyblok.FuretUI.Resource.List.query()
            query = query.filter_by(model=model)
            resource = query.one_or_none()
        else:
            resource_type = field.attrib.get('resource-type', 'set')
            resource_model = 'Model.FuretUI.Resource.%s' % (
                resource_type.capitalize())
            resource = self.anyblok.IO.Mapping.get(resource_model, resource)
            if not resource:
                for type_ in ('set', 'list', 'thumbnail'):
                    resource_model = 'Model.FuretUI.Resource.%s' % type_
                    resource = self.anyblok.IO.Mapping.get(
                        resource_model, resource)
                    if resource:
                        break

        if resource:
            description['resource'] = resource.id

        fields = self.anyblok.get(model).get_primary_keys()

        if description.get('slot'):
            fields.extend(description.pop('slot_fields'))

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

        lang = self.context.get('lang', 'en')
        for k, label in description['selections'].items():
            description['selections'][k] = Translation.get(
                lang, f"field:selection:{self.model}:{description['id']}",
                label)

        return self.get_field_for_(field, 'Selection', description, fields2read)

    def get_field_for_Country(self, field, description, fields2read):
        if pycountry is None:
            return self.get_field_for_(
                field, 'String', description, fields2read)

        description = deepcopy(description)
        mode = self.anyblok.loaded_namespaces_first_step[
            self.model][description['id']].mode
        description['selections'] = {
            getattr(country, mode): country.name
            for country in pycountry.countries}

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

        lang = self.context.get('lang', 'en')
        for k, label in description['selections'].items():
            description['selections'][k] = Translation.get(
                lang, f"field:selection:{self.model}:{description['id']}",
                label)

        for key in ('done-states', 'dangerous-states'):
            description[key] = [
                x.strip() for x in field.attrib.get(key, '').split(',')]

        return self.get_field_for_(field, 'StatusBar', description, fields2read)

    def replace_buttons(self, userid, template, fields_description,
                        fields2read, **kwargs):
        buttons = template.findall('.//button')
        for el in buttons:
            el.tag = kwargs.get('button_tag', 'furet-ui-form-button')
            config = {
                'label': el.attrib['label'],
                'class': el.attrib.get('class', '').split(),
            }
            if 'call' in el.attrib:
                call = el.attrib['call']
                if call not in self.anyblok.exposed_methods.get(self.model,
                                                                {}):
                    raise ResourceTemplateRendererException(
                        f"On resource {self.identity} : The button "
                        f"{config} define an unexposed method '{call}'"
                    )

                definition = self.anyblok.exposed_methods[self.model][call]
                permission = definition['permission']
                if permission is not None:
                    if not self.anyblok.FuretUI.check_acl(
                        self.model, permission
                    ):
                        el.getparent().remove(el)
                        return

                config['call'] = call
            elif 'open-resource' in el.attrib:
                resource = None
                for model in self.__class__.get_resource_types().keys():
                    resource = self.anyblok.IO.Mapping.get(
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

            self.extract_slot(el, fd, fields2read)
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
            fields = get_fields_from_string(value)
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
                el, fields2read, 'hidden', 'readonly')
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
                Model = self.anyblok.get(el.attrib['model'])
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

    def apply_roles_attributes_only_for_roles(self, roles, template):
        els = template.findall('.//*[@only-for-roles]')
        for el in els:
            expected_roles = set([
                x.strip() for x in el.attrib['only-for-roles'].split(',')])
            if roles & expected_roles:
                del el.attrib['only-for-roles']
            else:
                el.getparent().remove(el)

    def apply_roles_attributes_not_for_roles(self, roles, template):
        els = template.findall('.//*[@not-for-roles]')
        for el in els:
            expected_roles = set([
                x.strip() for x in el.attrib['not-for-roles'].split(',')])
            if roles & expected_roles:
                el.getparent().remove(el)
            else:
                del el.attrib['not-for-roles']

    def apply_roles_attributes_readonly_for_roles(self, roles, template):
        els = template.findall('.//*[@readonly-for-roles]')
        for el in els:
            expected_roles = set([
                x.strip() for x in el.attrib['readonly-for-roles'].split(',')])
            del el.attrib['readonly-for-roles']
            if roles & expected_roles:
                el.attrib['readonly'] = '1'

    def apply_roles_attributes_write_only_for_roles(self, roles, template):
        els = template.findall('.//*[@write-only-for-roles]')
        for el in els:
            expected_roles = set([
                x.strip()
                for x in el.attrib['write-only-for-roles'].split(',')])
            del el.attrib['write-only-for-roles']
            if not (roles & expected_roles):
                el.attrib['readonly'] = '1'

    def apply_roles_attributes(self, userid, template):
        roles = set(self.anyblok.Pyramid.get_roles(userid))
        self.apply_roles_attributes_only_for_roles(roles, template)
        self.apply_roles_attributes_not_for_roles(roles, template)
        self.apply_roles_attributes_readonly_for_roles(roles, template)
        self.apply_roles_attributes_write_only_for_roles(roles, template)

    def _encode_to_furetui(self, userid, template, fields_description,
                           fields2read, **kwargs):
        nsmap = {'v-bind': 'https://vuejs.org/'}
        etree.cleanup_namespaces(
            template, top_nsmap=nsmap, keep_ns_prefixes=['v-bind'])
        self.apply_roles_attributes(userid, template)
        self.replace_divs(template, fields2read)
        self.replace_selector(template, fields2read)
        self.replace_fieldsets(template, fields2read)
        self.replace_tabs(template, fields2read)
        self.replace_tab(template, fields2read)
        self.replace_fields(template, fields_description, fields2read)
        self.replace_buttons(userid, template, fields_description, fields2read,
                             **kwargs)

    def encode_to_furetui(self, userid, template, fields, fields2read,
                          **kwargs):
        Model = self.anyblok.get(self.model)
        fields_description = Model.fields_description(fields)
        self._encode_to_furetui(
            userid, template, fields_description, fields2read, **kwargs)

        if 'template_tag' in kwargs:
            template.tag = kwargs['template_tag']

        if 'template_class' in kwargs:
            template.set('class', kwargs['template_class'])

        tmpl = self.anyblok.furetui_templates.decode(
            html.tostring(template, encoding='unicode'))

        fields2data = re.findall(  # noqa: W605
            "\{\{\s*fields\.\w*\s*\}\}", tmpl)  # noqa W605
        for field2data in fields2data:
            field = get_fields_from_string(field2data)[0]
            tmpl = tmpl.replace(field2data, '{{ data.%s }}' % field)
            fields2read.append(field)

        return tmpl

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
            'Model.FuretUI.Resource.Singleton': 'Singleton',
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
        Mapping = self.anyblok.IO.Mapping
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

    def check_acl(self):
        if not self.code:
            return True

        type_ = self.type.label.lower()
        return self.anyblok.FuretUI.check_acl(self.code, type_)

    def get_menus(self):
        return self.anyblok.FuretUI.Menu.get_menus_from(resource=self)

    def get_translated_label_for(self, field, text):
        lang = self.context.get('lang', 'en')
        Model = self.anyblok.get(self.model)
        models = [self.model] + list(Model.__depends__)

        for model in models:
            res = Translation.get(lang, f"field:{model}:{field}", text)
            if res != text:
                return res

        return text


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

    def field_for_(self, field, fields2read, **kwargs):
        widget = kwargs.get('widget', field['type']).lower()
        res = {
            'hidden': False,
            'name': field['id'],
            'label': kwargs.get(
                'label',
                self.get_translated_label_for(field['id'], field['label'])),
            'component': kwargs.get('component', 'furet-ui-field'),
            'type': widget,
            'sticky': False,
            'numeric': (
                True if widget in ('integer', 'float', 'decimal') else False),
            'tooltip': kwargs.get('tooltip'),
        }
        for key in ('sortable', 'column-can-be-hidden', 'hidden-column',
                    'hidden', 'sticky', 'width', 'slot'):
            if key in kwargs:
                value = kwargs[key]
                if value == '':
                    res[key] = True
                else:
                    res[key] = value
                    fields2read.extend(get_fields_from_string(value))

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
        Model = self.anyblok.get(f['model'])
        # Mapping = cls.anyblok.IO.Mapping
        if 'slot' in kwargs:
            f['slot'] = kwargs.pop('slot')
            fields = kwargs.pop('slot_fields')
        elif 'display' in kwargs:
            display = kwargs['display']
            fields = get_fields_from_string(display)
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
            menu = self.anyblok.IO.Mapping.get(
                'Model.FuretUI.Menu.Resource', kwargs['menu'])
            resource = menu.resource
        elif 'resource' in kwargs:
            for type_ in ('Set', 'Form'):
                resource_model = 'Model.FuretUI.Resource.%s' % type_
                resource = self.anyblok.IO.Mapping.get(
                    resource_model, kwargs['resource'])
                if resource:
                    break
        else:
            query = self.anyblok.FuretUI.Resource.Form.query()
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

        lang = self.context.get('lang', 'en')
        for k, label in f['selections'].items():
            f['selections'][k] = Translation.get(
                lang, f"field:selection:{self.model}:{field['id']}",
                label)

        return self.field_for_(f, fields2read, **kwargs)

    def field_for_Country(self, field, fields2read, **kwargs):
        if pycountry is None:
            return self.field_for_Selection(
                field, fields2read, widget="String", **kwargs)

        mode = self.anyblok.loaded_namespaces_first_step[
            self.model][field['id']].mode
        selections = {getattr(country, mode): country.name
                      for country in pycountry.countries}

        return self.field_for_Selection(
            field, fields2read, widget="Selection", selections=str(selections),
            **kwargs)

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
            if call not in self.anyblok.exposed_methods.get(model, {}):
                raise ResourceTemplateRendererException(
                    f"On resource {self.identity} : The button "
                    f"{attributes} define an unexposed method '{call}'"
                )

            definition = self.anyblok.exposed_methods[model][call]
            permission = definition['permission']
            if permission is not None:
                if not self.anyblok.FuretUI.check_acl(model, permission):
                    return None

        elif 'open-resource' in attributes:
            resource = None
            for model in self.__class__.get_resource_types().keys():
                resource = self.anyblok.IO.Mapping.get(
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
            fields = get_fields_from_string(value)
            config[key] = value
            fields2read.extend(fields)

        if config:
            config['props'] = initial_props = {}
            for key in el.attrib:
                if key in attributes:
                    continue

                initial_props[key] = el.attrib.get(key)

        return config

    def clean_unnecessary_attributes(self, el, *allows):
        for key in el.attrib:
            if key not in allows:
                del el.attrib[key]

    def replace_divs(self, template, fields2read):
        nsmap = {'v-bind': 'https://vuejs.org/'}
        etree.cleanup_namespaces(
            template, top_nsmap=nsmap, keep_ns_prefixes=['v-bind'])
        fields = template.findall('.//div')
        for el in fields:
            config = self.update_interface_attributes(
                el, fields2read, 'hidden', 'readonly')
            if not config:
                continue

            el.tag = 'furet-ui-div'
            self.clean_unnecessary_attributes(el, 'class')
            el.attrib['{%s}resource' % el.nsmap['v-bind']] = "resource"
            el.attrib['{%s}data' % el.nsmap['v-bind']] = "data"
            el.attrib['{%s}config' % el.nsmap['v-bind']] = str(config)

    def extract_slot(self, field, attributes, fields2read):
        if not (bool(field.getchildren()) or bool(field.text)):
            return

        slot = deepcopy(field)
        slot.tag = 'div'
        self.replace_divs(slot, fields2read)

        for x in slot.attrib.keys():
            del slot.attrib[x]

        slot_str = etree.tostring(slot).decode('utf-8')
        fields = get_fields_from_string(slot_str)
        if fields:
            fields2read.extend(fields)
            for f in fields:
                slot_str = slot_str.replace('fields.%s' % f, 'data.%s' % f)

        attributes['slot'] = slot_str
        attributes['slot_fields'] = list(set(
            get_fields_from_string(slot_str, prefix='relation')))

    def get_definitions(self, **kwargs):
        Model = self.anyblok.get(self.model)
        fd = Model.fields_description()
        headers = []
        fields2read = []
        pks = Model.get_primary_keys()
        fields2read.extend(pks)
        buttons = []
        if self.template:
            template = self.anyblok.FuretUI.get_template(
                self.template, tostring=False)
            # FIXME button in header
            for field in template.findall('.//field'):
                attributes = deepcopy(field.attrib)
                self.extract_slot(field, attributes, fields2read)

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

        title = self.title
        mapping = self.anyblok.IO.Mapping.get_from_entry(self)
        if mapping and title:
            lang = self.context.get('lang', 'en')
            title = Translation.get(lang, f'resource:list:{mapping.key}', title)

        res = [{
            'id': self.id,
            'type': self.type.label.lower(),
            'title': title,
            'model': self.model,
            'filters': self.anyblok.FuretUI.Resource.Filter.get_for_resource(
                list=self),
            'tags': self.anyblok.FuretUI.Resource.Tags.get_for_resource(
                list=self),
            'buttons': buttons,
            # 'on_selected_buttons': [],  # TODO
            'headers': headers,
            'fields': fields2read,
        }]
        return res

    def get_i18n_to_export(self, external_id):
        if not self.title:
            return []

        return [(f'resource:list:{external_id}', self.title)]


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Thumbnail(
    Declarations.Model.FuretUI.Resource,
    Declarations.Mixin.Template
):
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use('id'))
    title = String()
    model = String(nullable=False, size=256,
                   foreign_key=Declarations.Model.System.Model.use('name'))
    template = String()

    def get_definitions(self, **kwargs):
        Model = self.anyblok.get(self.model)
        fd = Model.fields_description()
        pks = Model.get_primary_keys()
        userid = kwargs.get('authenticated_userid')
        buttons = []

        if self.template:
            template = self.anyblok.FuretUI.get_template(
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

        title = self.title
        mapping = self.anyblok.IO.Mapping.get_from_entry(self)
        if mapping and title:
            lang = self.context.get('lang', 'en')
            title = Translation.get(
                lang, f'resource:thumbnail:{mapping.key}', title)

        res = {
            'id': self.id,
            'type': self.type.label.lower(),
            'title': title,
            'model': self.model,
            'pks': pks,
            'filters': self.anyblok.FuretUI.Resource.Filter.get_for_resource(
                thumbnail=self),
            'tags': self.anyblok.FuretUI.Resource.Tags.get_for_resource(
                thumbnail=self),
            'buttons': buttons,
            # 'on_selected_buttons': [],  # TODO
        }
        fields2read = []
        fields2read.extend(pks)
        for tag in ('header', 'footer'):
            sub_template = template.find('./%s' % tag)
            if not sub_template:
                continue

            sub_template.tag = 'div'
            template.remove(sub_template)
            res['%s_template' % tag] = self.encode_to_furetui(
                userid, sub_template, fields, fields2read,
                template_tag=tag,
                template_class=f'card-{tag}',
                button_tag=f'furet-ui-thumbnail-{tag}-button'
            )

        body_template = self.encode_to_furetui(
            userid, template, fields, fields2read)
        fields2read = list(set(fields2read))
        fields2read.sort()
        res.update({
            'body_template': body_template,
            'fields': fields2read,
        })
        return [res]

    def get_i18n_to_export(self, external_id):
        if not self.title:
            return []

        return [(f'resource:thumbnail:{external_id}', self.title)]


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

    def to_dict(self, *a, **kw):
        res = super().to_dict(*a, **kw)
        if 'label' in res:
            mapping = self.anyblok.IO.Mapping.get_from_entry(self)
            if mapping:
                lang = self.context.get('lang', 'en')
                res['label'] = Translation.get(
                    lang, f'resource:filter:{mapping.key}', res['label'])

        return res

    def get_i18n_to_export(self, external_id):
        return [(f'resource:filter:{external_id}', self.label)]


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

    def to_dict(self, *a, **kw):
        res = super().to_dict(*a, **kw)
        if 'label' in res:
            mapping = self.anyblok.IO.Mapping.get_from_entry(self)
            if mapping:
                lang = self.context.get('lang', 'en')
                res['label'] = Translation.get(
                    lang, f'resource:tags:{mapping.key}', res['label'])

        return res

    def get_i18n_to_export(self, external_id):
        return [(f'resource:tags:{external_id}', self.label)]


@Declarations.register(Declarations.Mixin)  # noqa
class MixinForm:
    id = Integer(primary_key=True,
                 foreign_key=Declarations.Model.FuretUI.Resource.use(
                    'id').options(ondelete='cascade'))
    model = String(foreign_key=Declarations.Model.System.Model.use(
                    'name').options(ondelete='cascade'),
                   nullable=False, size=256)
    template = String()

    def get_classical_definitions(self, **kwargs):
        res = self.to_dict('id', 'type', 'model')
        userid = kwargs.get('authenticated_userid')
        Model = self.anyblok.get(self.model)
        fd = Model.fields_description()
        if self.template:
            template = self.anyblok.FuretUI.get_template(
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

    def get_i18n_to_export(self, external_id):
        return []


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Form(
    Declarations.Mixin.MixinForm,
    Declarations.Model.FuretUI.Resource,
    Declarations.Mixin.Template
):
    polymorphic_columns = String()
    # TODO field Selection RO / RW / WO

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
                'label': form.get_label(),
                'waiting_value': form.polymorphic_values,
                'resource_id': form.resource.id,
            })
            res.extend(form.resource.get_definitions(**kwargs))

        return res

    def get_primary_keys_for(self):
        return self.anyblok.get(self.model).get_primary_keys()

    def get_definitions(self, **kwargs):
        if self.polymorphic_columns:
            if not self.polymorphic_columns:
                raise Exception(
                    'No polymorphic_columns defined for %r' % self)

            return self.get_polymorphic_definitions(**kwargs)

        return self.get_classical_definitions(**kwargs)


@Declarations.register(Declarations.Model.FuretUI.Resource)
class PolymorphicForm:
    id = Integer(primary_key=True)
    label = String()
    parent = Many2One(model=Declarations.Model.FuretUI.Resource.Form,
                      one2many="forms")
    polymorphic_values = Json(nullable=False)
    resource = Many2One(model=Declarations.Model.FuretUI.Resource.Form)

    def get_label(self):
        if not self.label:
            return self.resource.model

        mapping = self.anyblok.IO.Mapping.get_from_entry(self)
        if not mapping:
            return self.label

        lang = self.context.get('lang', 'en')
        return Translation.get(
            lang, f'resource:polymorphicform:{mapping.key}', self.label)

    def get_i18n_to_export(self, external_id):
        if not self.label:
            return []

        return [(f'resource:polymorphicform:{external_id}', self.label)]


@Declarations.register(Declarations.Model.FuretUI.Resource)
class Singleton(
    Declarations.Mixin.MixinForm,
    Declarations.Model.FuretUI.Resource,
    Declarations.Mixin.Template
):

    def get_definitions(self, **kwargs):
        return self.get_classical_definitions(**kwargs)


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
        check_acl = self.anyblok.FuretUI.check_acl
        for acl in ('create', 'read', 'update', 'delete'):
            if getattr(self, 'can_%s' % acl):
                if not self.code:
                    definition['can_%s' % acl] = True
                else:
                    type_ = getattr(self, 'acl_%s' % acl)
                    definition['can_%s' % acl] = check_acl(self.code, type_)
            else:
                definition['can_%s' % acl] = False

        form_definitions = self.form.get_definitions(
            authenticated_userid=authenticated_userid)
        forms = []
        if self.form.polymorphic_columns:
            forms.extend(form_definitions[0]['forms'])

        definition.update({
            'forms': forms,
            'pks': self.form.get_primary_keys_for(),
            'form': self.form.id,
            'multi': getattr(self, self.multi_type).id,
        })
        res = [definition]
        res.extend(form_definitions)
        res.extend(getattr(self, self.multi_type).get_definitions(
            authenticated_userid=authenticated_userid))
        return res

    def check_acl(self):
        multi = getattr(self, self.multi_type)
        return multi.check_acl()

    def get_i18n_to_export(self, external_id):
        return []
