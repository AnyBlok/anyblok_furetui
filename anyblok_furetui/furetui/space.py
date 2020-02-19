# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.column import String


@Declarations.register(Declarations.Model.FuretUI)
class Space:
    code = String(primary_key=True)
    label = String(nullable=False)
    description = String()
    icon_code = String()
    icon_type = String()

    def get_path(self):
        return '/space/%s/resource/0' % self.code

    @classmethod
    def get_for_user(cls, authenticated_userid):
        query = cls.query()
        # TODO filter in function of access roles
        return query
