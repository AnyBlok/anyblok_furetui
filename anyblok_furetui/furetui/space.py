# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import json
from sqlalchemy import or_, text
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
        query = text("""
            with recursive menu_tree as (
                select
                    fm.id,
                    fm.order,
                    0 as parent_order,
                    fm.menu_type,
                    fm.parent_id,
                    fmr.label,
                    false as default
                from
                    furetui_menu fm
                    join furetui_menu_root fmr on fmr.id = fm.id
                where
                     fmr.space_code=:space_code

                union all

                select
                    child.id,
                    child.order,
                    (parent.parent_order + parent.order) as parent_order,
                    child.menu_type,
                    child.parent_id,
                    coalesce(node.label, resource.label) as label,
                    coalesce(resource.default, false) as default
                from
                    furetui_menu as child
                    left outer join furetui_menu_node as node
                        on node.id = child.id
                    left outer join furetui_menu_resource resource
                        on resource.id = child.id
                    join menu_tree as parent on parent.id = child.parent_id
                )
                select
                     id
                from
                    menu_tree
                where
                     menu_type = 'Model.FuretUI.Menu.Resource'
                     and "default" is :default
                order by
                     parent_order asc,
                     "order" asc,
                     id asc
                limit 1;
        """)

        # take the first default found
        res = self.anyblok.execute(
            query.bindparams(space_code=self.code, default=True)).fetchone()
        if res is None:
            res = self.anyblok.execute(query.bindparams(
                space_code=self.code, default=False)).fetchone()

        query = []
        if res:
            mre = self.anyblok.FuretUI.Menu.query().get(res[0])
            if mre.order_by:
                query.append('orders=%s' % mre.order_by)
            if mre.tags:
                query.append('tags=%s' % mre.tags)
            if mre.filters:
                query.append('filters=%s' % json.dumps(mre.filters))

        return '/space/%s/menu/%d/resource/%d?%s' % (
            self.code, mre.id if mre else 0, mre.resource.id if mre else 0,
            '&'.join(query))

    @classmethod
    def get_for_user(cls, authenticated_userid):
        roles = cls.anyblok.Pyramid.get_roles(authenticated_userid)
        query = cls.query().order_by(cls.order.asc())
        query = query.filter(or_(
            cls.role.in_(roles), cls.role.is_(None), cls.role == ''))
        return query

    def get_menus(self, authenticated_userid):
        return self.anyblok.FuretUI.Menu.get_menus_from(
            authenticated_userid, space=self)
