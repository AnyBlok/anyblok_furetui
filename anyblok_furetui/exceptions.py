# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import re
from lxml import html
from anyblok.mixin import MixinType
from anyblok_furetui.furetui.translate import Translation
from anyblok import Declarations


class ResourceTemplateRendererException(Exception):
    pass


class FuretUIExceptions:

    def __init__(self, registry):
        self.registry = registry

    def __getattribute__(self, key):
        if key in ('registry', 'export_i18n', 'compile'):
            return super().__getattribute__(key)

        if key in self.registry.furetui_exceptions:
            return self.registry.furetui_exceptions[key]

        raise KeyError(f'{key} is not existing FuretUI Exception')

    def export_i18n(self, namespace, base, po):
        FuretUIExceptionBase.export_i18n(namespace, base, po)

    def compile(self, lang='en'):
        for excpt in self.registry.furetui_exceptions.values():
            excpt.compiled = {}
            excpt.compile_entry(lang, 'title')
            excpt.compile_entry(lang, 'content')


class FuretUIExceptionBase(Exception):
    title = 'Error'
    content = None
    compiled = {}

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        super().__init__(
            f'{self.__class__.__name__} : {kwargs}')

    @classmethod
    def export_i18n(cls, namespace, base, po):
        def callback(attr):
            def _callback(text):
                context = f'exception:{namespace}:{attr}'
                entry = Translation.define(context, text)
                po.append(entry)

            return _callback

        for totranslate in ('title', 'content'):
            entry = getattr(base, totranslate, None)
            if entry is None:
                continue

            entry = f'<div>{entry}</div>'
            root = html.fromstring(entry)
            cls.compile_template_i18n(root, callback(totranslate))

    @classmethod
    def compile_template_i18n(cls, tmpl, action_callback):

        def minimify(text):
            if not text:
                return text

            text = text.replace('\n', '').replace('\n', '').strip()
            regex = "\{ *self.\w* *\}"  # noqa W605
            if re.findall(regex, text):
                return None

            return text

        def compile_template_i18n_rec(el):
            text = minimify(el.text)
            tail = minimify(el.tail)
            if text:
                el.text = action_callback(text)

            if tail:
                el.tail = action_callback(tail)

            for child in el.getchildren():
                compile_template_i18n_rec(child)

        compile_template_i18n_rec(tmpl)

    @classmethod
    def compile_entry(cls, lang, entry):
        if lang not in cls.compiled:
            cls.compiled[lang] = {}

        def callback(text):
            context = f'exception:{cls.__registry_name__}:{entry}'
            return Translation.get(lang, context, text)

        text = getattr(cls, entry)
        text = f'<div>{text}</div>'
        root = html.fromstring(text)
        cls.compile_template_i18n(root, callback)

        if entry == 'title':
            res = root.text
        else:
            res = html.tostring(root).decode('utf-8')

        cls.compiled[lang][entry] = res
        return res

    @classmethod
    def get_formated_entry(cls, entry):
        lang = cls.anyblok.FuretUI.context.get('lang', 'en')
        text = cls.compiled.get(lang, {}).get(entry)

        if not text:
            text = cls.compile_entry(lang, entry)

        return text

    def get_formated_title(self):
        return self.__class__.get_formated_entry('title').format(self=self)

    def get_formated_content(self):
        return self.__class__.get_formated_entry('content').format(self=self)

    def get_additional_data(self):
        return []

    def to_furetui(self):
        return {
            'type': 'USER_ERROR',
            'title': self.get_formated_title(),
            'message': self.get_formated_content(),
            'datas': self.get_additional_data(),
        }


@Declarations.add_declaration_type(
    isAnEntry=True, assemble="assemble_callback",
)
class FuretUIException(MixinType):
    """It is use to defined formated exception need by furetui

    * Add a new exception::

        @Declarations.register(Declarations.FuretUIExceptions)
        class MyException:
            title = "My exception"  # not required
            content = '''
              <ul>
                <li>Can be a html</li>
                <li>A simple text</li>
                <li>With or without any named parameter : {foo}</li>
              </ul>
            '''

    * Remove an exception::

        @Declaration.unregister(Declaration.FuretUIExceptions.MyException,
                                MyException)

    * Use the exception::

        raise self.anyblok.FuretUIExceptions.MyException(foo='bar')
    """
    autodoc_anyblok_bases = False

    @classmethod
    def assemble_callback(cls, registry):
        registry.furetui_exceptions = {}
        registry.FuretUIExceptions = FuretUIExceptions(registry)
        for exception in registry.loaded_registries["FuretUIException_names"]:
            ns = registry.loaded_registries[exception]
            bases = []
            bases.extend(ns['bases'])
            bases.append(FuretUIExceptionBase)
            bases.append(registry.registry_base)
            properties = ns.copy()
            name = exception.split('.')[-1]
            registry.furetui_exceptions[name] = excpt = type(
                exception, tuple(bases), properties)

            if not excpt.title:
                raise Exception(f'title is required on {excpt}')

            if not excpt.content:
                raise Exception(f'content is required on {excpt}')
