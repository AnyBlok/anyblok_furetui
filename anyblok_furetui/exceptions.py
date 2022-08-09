# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.mixin import MixinType
from anyblok import Declarations


class ResourceTemplateRendererException(Exception):
    pass


class FuretUIExceptions:

    def __init__(self, registry):
        self.registry = registry

    def __getattribute__(self, key):
        if key == 'registry':
            return super().__getattribute__(key)

        if key in self.registry.furetui_exceptions:
            return self.registry.furetui_exceptions[key]

        raise KeyError(f'{key} is not existing FuretUI Exception')


class FuretUIExceptionBase(Exception):
    title = 'Error'
    content = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        super().__init__(
            f'{self.__class__.__name__} : {kwargs}')

    def get_formated_title(self):
        # TODO i18n
        return self.title.format(self=self)

    def get_formated_content(self):
        # TODO i18n
        return self.content.format(self=self)

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
