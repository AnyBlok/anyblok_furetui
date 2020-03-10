# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import json
from sqlalchemy import or_
from anyblok.declarations import Declarations
from anyblok.column import String, Integer


@Declarations.register(Declarations.Model.FuretUI)
class Space:
    code = String(primary_key=True)
    label = String(nullable=False)
    role = String()
    order = Integer(default=100, nullable=False)
    description = String()
    icon_code = String()
    icon_type = String()

    def get_path(self):
        MRe = self.registry.FuretUI.Menu.Resource
        MRo = self.registry.FuretUI.Menu.Root
        query = MRe.query()
        # link with this space
        query = query.join(MRe.root)
        query = query.filter(MRo.space == self)
        # order
        query = query.order_by(MRo.order.asc())
        query = query.order_by(MRe.order.asc()).order_by(MRe.id.asc())
        # take the first default found
        mre = query.filter(MRe.default.is_(True)).first()
        if mre is None:
            mre = query.first()

        query = []
        if mre.order_by:
            query.append('order=%s' % mre.order_by)
        if mre.tags:
            query.append('tags=%s' % mre.tags)
        if mre.filters:
            query.append('filters=%s' % json.dumps(mre.filters))

        return '/space/%s/menu/%d/resource/%d?%s' % (
            self.code, mre.id if mre else 0, mre.resource.id if mre else 0,
            '&'.join(query))

    @classmethod
    def get_for_user(cls, authenticated_userid):
        roles = cls.registry.Pyramid.get_roles(authenticated_userid)
        query = cls.query().order_by(cls.order.asc())
        query = query.filter(or_(
            cls.role.in_(roles), cls.role.is_(None), cls.role == ''))
        return query

    def get_menus(self, authenticated_userid):
        menus = []
        MRe = self.registry.FuretUI.Menu.Resource
        MRo = self.registry.FuretUI.Menu.Root
        mros = MRo.query().filter(MRo.space == self)
        mros = mros.order_by(MRo.order.asc())
        for mro in mros:
            mres = MRe.query().filter(MRe.root == mro)
            mres = mres.order_by(MRe.order.asc()).order_by(MRe.id.asc())
            mres = mres.all()
            if not mres:
                continue

            mres = [{'resource': mre.resource.id,
                     **mre.to_dict('id', 'order', 'label', 'icon_code',
                                   'icon_type', 'tags', 'order_by', 'filters')}
                    for mre in mres
                    if mre.check_acl(authenticated_userid)]

            if not mres:
                continue

            if mro.label:
                menus.append(
                    {'children': mres, **mro.to_dict(
                        'id', 'order', 'label', 'icon_code', 'icon_type')})
            else:
                menus.extend(mres)

        return menus
