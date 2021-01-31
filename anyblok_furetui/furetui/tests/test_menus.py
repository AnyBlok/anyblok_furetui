# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from furl import furl


class Mixin:

    def import_space_definition(self, registry, with_default=True,
                                with_space=True):
        kwargs = {}
        resource = registry.FuretUI.Resource.Custom.insert(component='test')
        Menu = registry.FuretUI.Menu
        if with_space:
            space = registry.FuretUI.Space.insert(
                code="test", label="Test", description="Test")
            kwargs.update(dict(space=space))
        else:
            kwargs.update(dict(resource=resource))

        root1 = Menu.Root.insert(label="Root 1", order=20, **kwargs)
        node1 = Menu.Node.insert(label="Node 1")
        node1.children.extend([
            Menu.Resource.insert(label="Resource 1", resource=resource),
            Menu.Url.insert(label="Resource 2", url="http://anyblok.org"),
            Menu.Call.insert(label="Resource 3", model="Model.System.Blok",
                             method="furetui_install"),
        ])
        node2 = Menu.Node.insert(label="Node 2")
        node2.children.extend([
            Menu.Resource.insert(label="Resource 4", resource=resource),
            Menu.Resource.insert(label="Resource 5", resource=resource,
                                 default=with_default),
            Menu.Resource.insert(label="Resource 6", resource=resource),
        ])
        root1.children.extend([node1, node2])

        root2 = Menu.Root.insert(label="Root 2", order=10, **kwargs)
        root2.children.extend([
            Menu.Resource.insert(label="Resource 7", resource=resource),
            Menu.Url.insert(label="Resource 8", url="http://anyblok.org"),
            Menu.Call.insert(label="Resource 9", model="Model.System.Blok",
                             method="furetui_install"),
        ])
        return space if with_space else resource

    def checkMenus(self, registry, menus, with_resource=False):
        resource = registry.FuretUI.Resource.Custom.query().filter_by(
            component='test').one()

        def root_id(label):
            return registry.FuretUI.Menu.Root.query().filter_by(
                label=label).one().id

        def resource_id(label):
            return registry.FuretUI.Menu.Resource.query().filter_by(
                label=label).one().id

        def url_id(label):
            return registry.FuretUI.Menu.Url.query().filter_by(
                label=label).one().id

        def call_id(label):
            return registry.FuretUI.Menu.Call.query().filter_by(
                label=label).one().id

        def node_id(label):
            return registry.FuretUI.Menu.Node.query().filter_by(
                label=label).one().id

        assert menus == [
            {
                'icon_code': None,
                'icon_type': None,
                'id': root_id('Root 2'),
                'label': 'Root 2',
                'order': 10,
                'children': [
                    {
                        'children': [],
                        'filters': {},
                        'icon_code': None,
                        'icon_type': None,
                        'id': resource_id('Resource 7'),
                        'label': 'Resource 7',
                        'order': 100,
                        'order_by': None,
                        'resource': resource.id,
                        'tags': None
                    },
                    {
                        'children': [],
                        'icon_code': None,
                        'icon_type': None,
                        'id': url_id('Resource 8'),
                        'label': 'Resource 8',
                        'order': 100,
                        'url': furl('http://anyblok.org'),
                    },
                    {
                        'children': [],
                        'icon_code': None,
                        'icon_type': None,
                        'id': call_id('Resource 9'),
                        'label': 'Resource 9',
                        'method': 'furetui_install',
                        'model': 'Model.System.Blok',
                        'order': 100,
                        'resource': resource.id if with_resource else None,
                    },
                ],
            },
            {
                'icon_code': None,
                'icon_type': None,
                'id': root_id('Root 1'),
                'label': 'Root 1',
                'order': 20,
                'children': [
                    {
                        'icon_code': None,
                        'icon_type': None,
                        'id': node_id('Node 1'),
                        'label': 'Node 1',
                        'order': 100,
                        'children': [
                            {
                                'children': [],
                                'filters': {},
                                'icon_code': None,
                                'icon_type': None,
                                'id': resource_id('Resource 1'),
                                'label': 'Resource 1',
                                'order': 100,
                                'order_by': None,
                                'resource': resource.id,
                                'tags': None
                            },
                            {
                                'children': [],
                                'icon_code': None,
                                'icon_type': None,
                                'id': url_id('Resource 2'),
                                'label': 'Resource 2',
                                'order': 100,
                                'url': furl('http://anyblok.org'),
                            },
                            {
                                'children': [],
                                'icon_code': None,
                                'icon_type': None,
                                'id': call_id('Resource 3'),
                                'label': 'Resource 3',
                                'method': 'furetui_install',
                                'model': 'Model.System.Blok',
                                'order': 100,
                                'resource': (
                                    resource.id if with_resource else None
                                ),
                            }
                        ],
                    },
                    {
                        'children': [
                            {
                                'children': [],
                                'filters': {},
                                'icon_code': None,
                                'icon_type': None,
                                'id': resource_id('Resource 4'),
                                'label': 'Resource 4',
                                'order': 100,
                                'order_by': None,
                                'resource': resource.id,
                                'tags': None
                            },
                            {
                                'children': [],
                                'filters': {},
                                'icon_code': None,
                                'icon_type': None,
                                'id': resource_id('Resource 5'),
                                'label': 'Resource 5',
                                'order': 100,
                                'order_by': None,
                                'resource': resource.id,
                                'tags': None,
                            },
                            {
                                'children': [],
                                'filters': {},
                                'icon_code': None,
                                'icon_type': None,
                                'id': resource_id('Resource 6'),
                                'label': 'Resource 6',
                                'order': 100,
                                'order_by': None,
                                'resource': resource.id,
                                'tags': None,
                            }
                        ],
                        'icon_code': None,
                        'icon_type': None,
                        'id': node_id('Node 2'),
                        'label': 'Node 2',
                        'order': 100
                    }
                ],
            },
        ]


@pytest.mark.usefixtures('rollback_registry')
class TestMenuInSpace(Mixin):

    def test_get_path_with_default_value(self, rollback_registry):
        space = self.import_space_definition(rollback_registry)
        menu = rollback_registry.FuretUI.Menu.Resource.query().filter_by(
            label='Resource 5').one()
        resource = rollback_registry.FuretUI.Resource.Custom.query().filter_by(
            component='test').one()
        path = space.get_path()
        assert path == '/space/test/menu/%d/resource/%d?' % (
            menu.id, resource.id)

    def test_get_path_without_default_value(self, rollback_registry):
        space = self.import_space_definition(
            rollback_registry, with_default=False)
        menu = rollback_registry.FuretUI.Menu.Resource.query().filter_by(
            label='Resource 7').one()
        resource = rollback_registry.FuretUI.Resource.Custom.query().filter_by(
            component='test').one()
        path = space.get_path()
        assert path == '/space/test/menu/%d/resource/%d?' % (
            menu.id, resource.id)

    def test_get_menus(self, rollback_registry):
        space = self.import_space_definition(rollback_registry)
        menus = space.get_menus('')
        self.checkMenus(rollback_registry, menus)

    def test_for_user(self, rollback_registry):
        space = self.import_space_definition(rollback_registry)
        spaces = space.get_for_user('')
        assert spaces.all().code == ['test']


@pytest.mark.usefixtures('rollback_registry')
class TestMenuInResource(Mixin):

    def test_get_menus(self, rollback_registry):
        resource = self.import_space_definition(
            rollback_registry, with_space=False)
        menus = resource.get_menus('')
        self.checkMenus(rollback_registry, menus, with_resource=True)
