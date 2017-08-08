# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import String, Boolean, Integer

register = Declarations.register
Model = Declarations.Model


@register(Model.Web)
class Action:

    id = Integer(primary_key=True)
    model = String(foreign_key=Model.System.Model.use('name'), nullable=False)
    label = String(nullable=False)
    add_delete = Boolean(default=True)
    add_new = Boolean(default=True)
    add_edit = Boolean(default=True)

    def get_selected_view_modes(self):
        return ['Model.Web.View.List', 'Model.Web.View.Thumbnail']

    def get_selected_view(self):
        View = self.registry.Web.View
        query = View.query().filter(View.id.in_([v.id for v in self.views]))
        query = query.filter(View.mode.in_(self.get_selected_view_modes()))
        query = query.order_by(View.order)
        return query.first().id

    def render(self):
        views = [
            {
                'viewId': str(v.id),
                'type': v.mode.split('.')[-1],
                'unclickable': v.mode not in self.get_selected_view_modes(),
            }
            for v in self.views
        ]
        if not views:
            views = [
                {
                    'viewId': 'List-%d' % self.id,
                    'type': 'List',
                },
                {
                    'viewId': 'Form-%d' % self.id,
                    'type': 'Form',
                    'unclickable': True,
                },
            ]
            selected_view = 'List-%d' % self.id
        else:
            selected_view = self.get_selected_view()

        return {
            'type': 'UPDATE_ACTION',
            'actionId': str(self.id),
            'label': self.label,
            'views': views,
            'selected_view': selected_view,
        }
