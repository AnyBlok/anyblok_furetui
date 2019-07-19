# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from logging import getLogger


logger = getLogger(__name__)


@Declarations.register(Declarations.Model)
class FuretUI:

    @classmethod
    def get_global(cls, authenticated_userid):
        res = super(FuretUI, cls).get_global(authenticated_userid)
        query = cls.registry.User.Role.query()
        res.update({
            'roles': [
                {
                    'name': role.name,
                    'label': role.label,
                    'depends': role.roles_name,
                }
                for role in query
            ]
        })
        if authenticated_userid:
            user = cls.registry.User.query().get(authenticated_userid)
            res.update({
                'userName': "%s %s" % (user.first_name,
                                       (user.last_name or '').upper()),
                'userRoles': user.get_roles(user.login),
                'authenticated': True,
            })

        return res
