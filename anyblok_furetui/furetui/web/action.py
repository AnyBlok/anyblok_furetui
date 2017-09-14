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

    def get_selected_view(self):
        View = self.registry.Web.View
        query = View.query().filter(View.id.in_([v.id for v in self.views]))
        query = query.order_by(View.order)
        return [v.id for v in query.all() if v.unclickable][0]

    def render(self):
        views = self.__class__.get_default_views_linked_with_action(
            action=self)
        selected_view = views[0]['viewId']
        return {
            'type': 'UPDATE_ACTION',
            'actionId': str(self.id),
            'label': self.label,
            'views': views,
            'selected_view': selected_view,
        }
