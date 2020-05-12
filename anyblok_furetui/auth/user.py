# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.field import Function


@Declarations.register(Declarations.Model.Pyramid)
class User:
    active = Function(fget='fget_active', fexpr='fexpr_active')

    def fget_active(self):
        credential = self.registry.Pyramid.CredentialStore.query().filter_by(
            login=self.login).one_or_none()

        return True if credential else False

    @classmethod
    def fexpr_active(cls):
        return cls.registry.Pyramid.CredentialStore.login == cls.login
