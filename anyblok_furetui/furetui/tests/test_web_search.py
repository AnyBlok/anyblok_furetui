# This file is a part of the AnyBlok / FuretUI project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import BlokTestCase


class TestWebSearch(BlokTestCase):

    def test_format_for_furetui(self):
        Search = self.registry.Web.Action.Search
        search = Search.insert(fieldname="name")
        self.assertEqual(
            search.format_for_furetui('Model.System.Model'),
            {
                'fieldname': 'name',
                'key': 'name',
                'label': 'Name',
                'model': 'Model.System.Model',
                'type': 'search',
            }
        )

    def test_format_for_furetui_with_foreign_key(self):
        Search = self.registry.Web.Action.Search
        search = Search.insert(fieldname="name", path="model")
        self.assertEqual(
            search.format_for_furetui('Model.Web.Action'),
            {
                'fieldname': 'name',
                'key': 'model.name',
                'label': 'Name',
                'model': 'Model.System.Model',
                'type': 'search',
            }
        )

    def test_format_for_furetui_with_relation_ship(self):
        Search = self.registry.Web.Action.Search
        search = Search.insert(fieldname="label", path="action")
        self.assertEqual(
            search.format_for_furetui('Model.Web.View'),
            {
                'fieldname': 'label',
                'key': 'action.label',
                'label': 'Label',
                'model': 'Model.Web.Action',
                'type': 'search',
            }
        )

    def test_format_for_furetui_with_relation_ship_and_foreign_key(self):
        Search = self.registry.Web.Action.Search
        search = Search.insert(fieldname="name", path="action.model")
        self.assertEqual(
            search.format_for_furetui('Model.Web.View.List'),
            {
                'fieldname': 'name',
                'key': 'action.model.name',
                'label': 'Name',
                'model': 'Model.System.Model',
                'type': 'search',
            }
        )

    def test_get_from_action(self):
        Action = self.registry.Web.Action
        action = Action.insert(model="Model.System.Model", label="Model")
        Action.Search.insert(fieldname="name", action=action)
        self.maxDiff = None
        self.assertEqual(
            Action.Search.get_from_action(action),
            [
                {
                    'fieldname': 'name',
                    'key': 'name',
                    'label': 'Name',
                    'model': 'Model.System.Model',
                    'type': 'search',
                },
            ]
        )

    def test_get_from_List_1(self):
        Action = self.registry.Web.Action
        List = self.registry.Web.View.List
        action = Action.insert(model="Model.System.Model", label="Model")
        view = List.insert(template='test', action=action)
        Action.Search.insert(fieldname="name", action=action)
        self.maxDiff = None
        self.assertEqual(
            Action.Search.get_from_view(view),
            [
                {
                    'fieldname': 'name',
                    'key': 'name',
                    'label': 'Name',
                    'model': 'Model.System.Model',
                    'type': 'search',
                },
            ]
        )

    def test_get_from_List_2(self):
        Action = self.registry.Web.Action
        List = self.registry.Web.View.List
        action = Action.insert(model="Model.System.Model", label="Model")
        view = List.insert(template='test', action=action)
        Action.Search.insert(fieldname="name", view=view)
        self.maxDiff = None
        self.assertEqual(
            Action.Search.get_from_view(view),
            [
                {
                    'fieldname': 'name',
                    'key': 'name',
                    'label': 'Name',
                    'model': 'Model.System.Model',
                    'type': 'search',
                },
            ]
        )
