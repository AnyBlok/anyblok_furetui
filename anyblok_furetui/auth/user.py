# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.column import Selection
from anyblok.field import Function


@Declarations.register(Declarations.Model)
class FuretUI:

    @classmethod
    def get_authenticated_userid_locale(cls, authenticated_userid):
        res = super(FuretUI, cls).get_authenticated_userid_locale(
            authenticated_userid)
        user = cls.registry.Pyramid.User.query().get(authenticated_userid)
        return user.lang or res

    @classmethod
    def user_management(cls, login, password, roles):
        Pyramid = cls.registry.Pyramid
        user = Pyramid.User.query().get(login)
        if user is None:
            user = Pyramid.User.insert(login=login)

        if password:
            cs = Pyramid.CredentialStore.query().get(login)
            if cs is None:
                Pyramid.CredentialStore.insert(
                    login=login, password=password)
            elif cs.password != password:
                cls.password = password

        for role_name in roles:
            role = Pyramid.Role.query().filter_by(name=role_name).one()
            user.append(role)


@Declarations.register(Declarations.Model.Pyramid)
class User:
    active = Function(fget='fget_active', fexpr='fexpr_active')
    lang = Selection(selections='get_languages')

    @classmethod
    def get_languages(cls):
        return {x: f'language.{x}' for x in cls.get_languages_code()}

    @classmethod
    def get_languages_code(cls):
        return ['en', 'fr']

    def fget_active(self):
        credential = self.registry.Pyramid.CredentialStore.query().filter_by(
            login=self.login).one_or_none()

        return True if credential else False

    @classmethod
    def fexpr_active(cls):
        return cls.registry.Pyramid.CredentialStore.login == cls.login
