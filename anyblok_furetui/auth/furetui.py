# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Pierre Verkest <pierreverkest84@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations


@Declarations.register(Declarations.Model)
class FuretUI:

    @classmethod
    def check_acl(cls, userid, resource, permission):
        return cls.registry.Pyramid.check_acl(userid, resource, permission)
