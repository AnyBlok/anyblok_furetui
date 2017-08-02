# This file is a part of the AnyBlok / FuretUI project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid.tests.testcase import PyramidBlokTestCase


class TestViewSpace(PyramidBlokTestCase):

    def create_menus(self, space, position):
        Menu = self.registry.Web.Menu
        menu1 = Menu.insert(
            label='Menu 1', icon='menu1', position=position, space=space
        )
        Menu.insert(label='Menu 1_1', icon='menu11',  parent=menu1)
        Menu.insert(label='Menu 1_2', icon='menu12',  parent=menu1)
        Menu.insert(label='Menu 1_3', icon='menu13',  parent=menu1)
        Menu.insert(label='Menu 1_4', icon='menu14',  parent=menu1)
        menu2 = Menu.insert(
            label='Menu 2', icon='menu2', position=position, space=space
        )
        Menu.insert(label='Menu 2_1', icon='menu21',  parent=menu2)
        Menu.insert(label='Menu 2_2', icon='menu22',  parent=menu2)
        Menu.insert(label='Menu 2_3', icon='menu23',  parent=menu2)
        Menu.insert(label='Menu 2_4', icon='menu24',  parent=menu2)

    def create_action(self, space):
        Action = self.registry.Web.Action
        action = Action.insert(model="Model.System.Model", label="Model")
        space.default_action = action

    def create_menu(self, space):
        Menu = self.registry.Web.Menu
        self.create_action(space)
        menu = Menu.insert(
            label='Menu 1', icon='menu1', space=space,
            action=space.default_action
        )
        space.default_menu = menu

    def create_space(self, left_menu=False, right_menu=False, action=False,
                     menu=False):
        Space = self.registry.Web.Space
        Category = Space.Category
        category = Category.insert(label="Test Category", icon="categ")
        space = Space.insert(
            label='Test Space', icon="space", description="Test",
            category=category
        )
        if left_menu:
            self.create_menus(space, 'left')
        elif right_menu:
            self.create_menus(space, 'right')

        if action:
            self.create_action(space)
            return space.id, space.default_action.id

        if menu:
            self.create_menu(space)
            return space.id, space.default_menu.id, space.default_action.id

        return space.id

    def assertSpaceData(self, res, space_id, left_menu=False, right_menu=False):
        M = self.registry.Web.Menu
        space = self.registry.Web.Space.query().get(space_id)
        _left_menu = M.getMenusForSpace(space, 'left') if left_menu else []
        _right_menu = M.getMenusForSpace(space, 'right') if right_menu else []
        self.assertEqual(
            res,
            {
                'type': 'UPDATE_SPACE',
                'spaceId': str(space_id),
                'left_menu': _left_menu,
                'right_menu': _right_menu,
            }
        )

    def assertSpace(self, **kwargs):
        webserver = self.webserver
        space_id = self.create_space(**kwargs)
        resp = webserver.post_json('/furetui/space/%d' % space_id, {})
        self.assertEqual(resp.status, '200 OK')
        self.assertSpaceData(resp.json[0], space_id, **kwargs)
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': '/space/%d' % space_id,
            }
        )

    def test_space_without_menu(self):
        self.assertSpace()

    def test_space_with_left_menu(self):
        self.assertSpace(left_menu=True)

    def test_space_with_rigth_menu(self):
        self.assertSpace(right_menu=True)

    def test_space_with_action(self):
        webserver = self.webserver
        space_id, action_id = self.create_space(action=True)
        resp = webserver.post_json('/furetui/space/%d' % space_id, {})
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': '/space/%d/action/%d' % (space_id, action_id),
            }
        )

    def test_space_with_menu(self):
        webserver = self.webserver
        space_id, menu_id, action_id = self.create_space(menu=True)
        resp = webserver.post_json('/furetui/space/%d' % space_id, {})
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': '/space/%d/menu/%d/action/%d' % (
                    space_id, menu_id, action_id
                ),
            }
        )

    def test_space_with_action_and_existing_action(self):
        webserver = self.webserver
        space_id, action_id = self.create_space(action=True)
        resp = webserver.post_json(
            '/furetui/space/%d' % space_id, {'actionId': 'test'}
        )
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': '/space/%d/action/test' % space_id,
            }
        )

    def test_space_with_menu_and_existing_action(self):
        webserver = self.webserver
        space_id, menu_id, action_id = self.create_space(menu=True)
        resp = webserver.post_json(
            '/furetui/space/%d' % space_id,
            {'menuId': 'test1', 'actionId': 'test2'}
        )
        self.assertEqual(
            resp.json[1],
            [
                {
                    'type': 'UPDATE_ROUTE',
                    'path': '/space/%d/menu/test1/action/test2' % space_id,
                },
            ]
        )

    def test_space_with_route_menu(self):
        webserver = self.webserver
        space_id = self.create_space()
        resp = webserver.post_json(
            '/furetui/space/%d' % space_id, {'menuId': 'test'}
        )
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': '/space/%d/menu/test' % space_id,
            }
        )

    def test_space_with_route_menu_and_action(self):
        webserver = self.webserver
        space_id = self.create_space()
        resp = webserver.post_json(
            '/furetui/space/%d' % space_id,
            {
                'menuId': 'test1',
                'actionId': 'test2',
            }
        )
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': '/space/%d/menu/test1/action/test2' % space_id,
            }
        )

    def test_space_with_route_menu_and_action_and_view(self):
        webserver = self.webserver
        space_id = self.create_space()
        resp = webserver.post_json(
            '/furetui/space/%d' % space_id,
            {
                'menuId': 'test1',
                'actionId': 'test2',
                'viewId': 'test3',
            }
        )
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': (
                    '/space/%d/menu/test1/action/test2/view/test3'
                ) % space_id,
            }
        )

    def test_space_with_route_menu_and_action_and_view_dataId_and_mode(self):
        webserver = self.webserver
        space_id = self.create_space()
        resp = webserver.post_json(
            '/furetui/space/%d' % space_id,
            {
                'menuId': 'test1',
                'actionId': 'test2',
                'viewId': 'test3',
                'dataId': 'test4',
                'mode': 'test5',
            }
        )
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': (
                    "/space/%d/menu/test1/action/test2/view/test3"
                    "/data/test4/mode/test5"
                ) % space_id,
            }
        )

    def test_space_with_route_action_and_view(self):
        webserver = self.webserver
        space_id = self.create_space()
        resp = webserver.post_json(
            '/furetui/space/%d' % space_id,
            {
                'actionId': 'test2',
                'viewId': 'test3',
            }
        )
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': (
                    '/space/%d/action/test2/view/test3'
                ) % space_id,
            }
        )

    def test_space_with_route_action_and_view_dataId_and_mode(self):
        webserver = self.webserver
        space_id = self.create_space()
        resp = webserver.post_json(
            '/furetui/space/%d' % space_id,
            {
                'actionId': 'test2',
                'viewId': 'test3',
                'dataId': 'test4',
                'mode': 'test5',
            }
        )
        self.assertEqual(
            resp.json[1],
            {
                'type': 'UPDATE_ROUTE',
                'path': (
                    "/space/%d/action/test2/view/test3"
                    "/data/test4/mode/test5"
                ) % space_id,
            }
        )
