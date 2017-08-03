# This file is a part of the AnyBlok / FuretUI project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidBlokTestCase
from lxml import html


class TestViewView(PyramidBlokTestCase):

    def test_unexisting_view(self):
        Action = self.registry.Web.Action
        action = Action.insert(model="Model.System.Model", label="Model")
        webserver = self.webserver
        resp = webserver.post_json('/furetui/view/List-%d' % action.id, {
            'actionId': action.id,
            'viewId': 'List-%d' % action.id
        })
        self.assertEqual(
            resp.json,
            [
                {
                    'buttons': [],
                    'creatable': True,
                    'deletable': True,
                    'editable': True,
                    'fields': ['is_sql_model', 'name', 'table'],
                    'headers': [
                        {
                            'component': 'furet-ui-list-field-boolean',
                            'label': 'Is a SQL model',
                            'name': 'is_sql_model',
                        },
                        {
                            'component': 'furet-ui-list-field-string',
                            'label': 'Name',
                            'name': 'name',
                        },
                        {
                            'component': 'furet-ui-list-field-string',
                            'label': 'Table',
                            'name': 'table',
                        },
                    ],
                    'model': 'Model.System.Model',
                    'onSelect': 'Form-%d' % action.id,
                    'onSelect_buttons': [],
                    'search': [
                        {
                            'key': 'is_sql_model',
                            'label': 'Is a SQL model',
                            'type': 'search',
                        },
                        {
                            'key': 'name',
                            'label': 'Name',
                            'type': 'search',
                        },
                        {
                            'key': 'table',
                            'label': 'Table',
                            'type': 'search',
                        },
                    ],
                    'selectable': False,
                    'type': 'UPDATE_VIEW',
                    'viewId': 'List-%d' % action.id,
                    'viewType': 'List',
                }
            ]
        )

    def test_existing_view(self):
        Action = self.registry.Web.Action
        View = self.registry.Web.View
        action = Action.insert(model="Model.System.Model", label="Model")
        view = View.insert(action=action, template="test_form_model",
                           mode='Model.Web.View.Form')
        et = html.fromstring(
            """
                <template id="test_form_model">
                    <field name="name" />
                    <field name="table" />
                </template>
            """
        )
        self.registry.furetui_views.load_template(et)
        self.registry.furetui_views.compile()
        webserver = self.webserver
        resp = webserver.post_json('/furetui/view/%d' % view.id, {})
        self.assertEqual(
            resp.json,
            [
                {
                    'buttons': [],
                    'creatable': True,
                    'deletable': True,
                    'editable': True,
                    'fields': ['name', 'table'],
                    'model': 'Model.System.Model',
                    'onSelect_buttons': [],
                    'template': (
                        '<div xmlns:v-bind="https://vuejs.org/" '
                        'id="test_form_model"><furet-ui-form-field-string name="name" '
                        'label="Name" required="0" '
                        'v-bind:config="config"></furet-ui-form-field-string>\n'
                        '                    <furet-ui-form-field-string name="table" '
                        'label="Table" required="1" '
                        'v-bind:config="config"></furet-ui-form-field-string>\n'
                        '                </div>\n'
                        '            '
                    ),
                    'type': 'UPDATE_VIEW',
                    'viewId': str(view.id),
                    'viewType': 'Form'
                }
            ]
        )
