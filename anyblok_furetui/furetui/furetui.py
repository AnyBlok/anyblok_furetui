# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2020 Pierre Verkest <pierreverkest84@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import polib
from os import path
from pathlib import Path
from datetime import datetime
from anyblok.declarations import Declarations
from anyblok_furetui import ResourceTemplateRendererException
from pyramid.httpexceptions import HTTPForbidden
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request
from .template import Template
from .translate import Translation
from anyblok.blok import BlokManager
from anyblok.config import Configuration
from os.path import join
from logging import getLogger


logger = getLogger(__name__)


def update_translation(i18n, translations, path=""):
    for key, value in translations.items():
        if not isinstance(key, str):
            raise Exception(
                "The key %r of the path %r must be a string" % key, path)
        elif isinstance(value, dict):
            node = i18n.setdefault(key, {})
            path += key + '.'
            update_translation(node, value)
        elif not isinstance(value, str):
            path += key
            raise Exception(
                "The value %r of the path %r must be a string" % value, path)
        else:
            i18n[key] = value


@Declarations.register(Declarations.Model)
class FuretUI:

    @classmethod
    def import_i18n(cls, lang):
        reload_at_change = Configuration.get('pyramid.reload_all', False)
        if Translation.has_lang(lang) and not reload_at_change:
            return

        Blok = cls.anyblok.System.Blok
        for blok in Blok.list_by_state('installed'):
            bpath = BlokManager.getPath(blok)
            if path.exists(path.join(bpath, 'locale', f'{lang}.po')):
                po = polib.pofile(path.join(bpath, 'locale', f'{lang}.po'))
                for entry in po:
                    Translation.set(lang, entry)

    @classmethod
    def pre_load(cls, lang='en'):
        logger.info('Preload furet UI component')
        templates = Template()
        i18n = {}
        Blok = cls.anyblok.System.Blok
        for blok in Blok.list_by_state('installed'):
            b = BlokManager.get(blok)
            bpath = BlokManager.getPath(blok)
            if hasattr(b, 'furetui'):
                for template in b.furetui.get('templates', []):
                    with open(join(bpath, template), 'r') as fp:
                        templates.load_file(fp)

                for local, translations in b.furetui.get('i18n', {}).items():
                    node = i18n.setdefault(local, {})
                    update_translation(node, translations)

        cls.import_i18n(lang)
        templates.compile(lang=lang)
        cls.anyblok.furetui_templates = templates
        cls.anyblok.furetui_i18n = i18n

    @classmethod
    def get_template(cls, *args, **kwargs):
        lang = cls.context.get('lang', 'en')
        reload_at_change = Configuration.get('pyramid.reload_all', False)
        if reload_at_change:
            if cls.context.get('reload_template', True):
                cls.pre_load(lang=lang)

        return cls.anyblok.furetui_templates.get_template(
            *args, lang=lang, **kwargs)

    @classmethod
    def export_i18n(cls, blok_name):
        b = BlokManager.get(blok_name)
        bpath = BlokManager.getPath(blok_name)
        po = polib.POFile()
        po.metadata = {
            'Project-Id-Version': b.version,
            'POT-Creation-Date': datetime.now().isoformat(),
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }
        if hasattr(b, 'furetui'):
            templates = Template()
            for template in b.furetui.get('templates', []):
                with open(join(bpath, template), 'r') as fp:
                    templates.load_file(fp, ignore_missing_extend=True)

            templates.export_i18n(po)

        Mapping = cls.anyblok.IO.Mapping
        for mapping in Mapping.query().filter_by(blokname=blok_name):
            obj = Mapping.get(mapping.model, mapping.key)
            for context, text in obj.get_i18n_to_export(mapping.key):
                entry = polib.POEntry(
                    msgctxt=context,
                    msgid=text,
                    msgstr='',
                )
                po.append(entry)

        Path(path.join(bpath, 'locale')).mkdir(exist_ok=True)
        po.save(path.join(bpath, 'locale', f'{blok_name}.pot'))

    @classmethod
    def get_default_path(cls, authenticated_userid):
        # TODO add default path on user
        return '/'

    @classmethod
    def get_user_informations(cls, authenticated_userid):
        query = cls.anyblok.FuretUI.Space.get_for_user(authenticated_userid)
        lang = cls.context.get('lang', 'en')

        def translate(space, field):
            text = getattr(space, field)
            mapping = cls.anyblok.IO.Mapping.get_from_entry(space)
            if not mapping:
                return text

            return Translation.get(lang, f'space:{mapping.key}:{field}', text)

        return [
            {
                'type': 'LOGIN',
                'userName': authenticated_userid,
            },
            {
                'type': 'UPDATE_USER_MENUS',
                'menus': [],
            },
            {
              'type': 'UPDATE_ROOT_MENUS',
              'menus': [
                  {
                      'code': x.code,
                      'label': translate(x, 'label'),
                      'icon': {
                          'code': x.icon_code,
                          'type': x.icon_type,
                      },
                      'description': translate(x, 'description'),
                      'path': x.get_path(),
                  }
                  for x in query
              ],
            },
        ]

    @classmethod
    def get_logout(cls):
        return [
            {'type': 'UPDATE_USER_MENUS', 'menus': []},
            {'type': 'UPDATE_ROOT_MENUS', 'menus': []},
            {'type': 'LOGOUT'},
            {'type': 'UPDATE_ROUTE', 'path': '/'},
            {'type': 'UPDATE_SPACE_MENUS', 'menus': []}
        ]

    @classmethod
    def get_authenticated_userid_locale(cls, authenticated_userid):
        return Configuration.get('furetui_default_locale', 'en')

    @classmethod
    def get_initialize(cls, authenticated_userid):
        res = []
        locales = {'en'}
        if not authenticated_userid:
            locale = Configuration.get('furetui_default_locale', 'en')
        else:
            locale = cls.get_authenticated_userid_locale(authenticated_userid)
            res.extend(cls.get_user_informations(authenticated_userid))

        cls.import_i18n(locale)
        cls.anyblok.furetui_templates.compile(lang=locale)

        locales.add(locale)
        res.extend([
            {'type': 'SET_LOCALE', 'locale': locale},
            {'type': 'UPDATE_LOCALES', 'locales': [
                {'locale': locale,
                 'messages': cls.anyblok.furetui_i18n.get(locale, {})}
                for locale in locales]},
            {'type': 'SET_LOGIN_PAGE',
             'login_page': Configuration.get('furetui_login_page', 'password')}
        ])
        return res

    @classmethod
    def check_security(cls, request):
        return True

    @classmethod
    def get_exposed_method_options(cls, request, permission, resource, model,
                                   call, data, pks):

        def get_resource():
            if resource == '0':
                return None

            return cls.anyblok.FuretUI.Resource.query().get(int(resource))

        res = [
            ('request', request),
            ('authenticated_userid', request.authenticated_userid),
            ('resource', get_resource),
        ]
        return res

    @classmethod
    def set_user_context(cls, authenticated_userid):
        cls.context.set({'userid': authenticated_userid})

    @classmethod
    def check_acl(cls, resource, permission):
        userid = cls.context.get('userid')
        return cls.anyblok.Pyramid.check_acl(userid, resource, permission)

    @classmethod
    def call_exposed_method(cls, request, resource=None, model=None, call=None,
                            data=None, pks=None):
        if call not in cls.anyblok.exposed_methods.get(model, {}):
            raise HTTPForbidden(f"the method '{call}' is not exposed")

        def apply_value(value):
            return value() if callable(value) else value

        options = {}
        definition = cls.anyblok.exposed_methods[model][call]
        permission = definition['permission']
        userId = request.authenticated_userid
        if permission is not None:
            if not cls.check_acl(model, permission):
                raise HTTPForbidden(
                    f"User '{userId}' has to be granted '{permission}' "
                    f"permission in order to call this method '{call}' on "
                    f"model '{model}'."
                )

        obj = cls.anyblok.get(model)
        if definition['is_classmethod'] is False:
            obj = obj.from_primary_keys(**pks)

        for (key, value) in cls.get_exposed_method_options(
            request, permission, resource, model, call, data, pks
        ):
            if definition[key] is True:
                options[key] = apply_value(value)
            elif definition[key]:
                options[definition[key]] = apply_value(value)

        res = None
        if not data:
            data = {}
        with saved_errors_in_request(request):
            res = getattr(obj, call)(**options, **data)

        return res

    @classmethod
    def validate_resources(cls):
        res = []
        with cls.context.set(reload_template=False):
            res.extend(cls.validate_form_resources())
            res.extend(cls.validate_list_resources())
            # TODO thumbnail, kanban

        return res

    @classmethod
    def validate_form_resources(cls):
        res = []
        Form = cls.anyblok.FuretUI.Resource.Form
        for resource in Form.query().filter(Form.template.isnot(None)):
            try:
                resource.get_definitions()
            except ResourceTemplateRendererException as e:
                logger.error(str(e))
                res.append(e)
            except Exception as e:
                logger.exception(str(e))
                raise

        return res

    @classmethod
    def validate_list_resources(cls):
        res = []
        List = cls.anyblok.FuretUI.Resource.List
        for resource in List.query().filter(List.template.isnot(None)):
            try:
                resource.get_definitions()
            except ResourceTemplateRendererException as e:
                logger.error(str(e))
                res.append(e)
            except Exception as e:
                logger.exception(str(e))
                raise

        return res

    @classmethod
    def user_management(cls, login, password, roles):
        raise NotImplementedError('This method must be overwrite')

    @classmethod
    def get_logo_path(cls):
        return '/furetui/static/images/logo.png'
