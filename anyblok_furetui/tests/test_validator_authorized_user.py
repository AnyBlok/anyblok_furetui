# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#    Copyright (C) 2020 Pierre Verkest <pierreverkest84@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok import Declarations
from anyblok.column import String
from anyblok_furetui import exposed_method
from anyblok.tests.conftest import init_registry_with_bloks, reset_db


register = Declarations.register
Model = Declarations.Model


class Mixin:

    def call(self, webserver, call, status=200):
        url = f'/furet-ui/resource/0/model/Model.Test/call/{call}'
        params = {'data': {'param': 1}, 'pks': {'code': 'test'}}
        return webserver.post_json(url, params, status=status)


def add_context_with_furetui():
    @register(Model)
    class Test:

        code = String(primary_key=True)

        @exposed_method(is_classmethod=False)
        def on_method(self, param=None):
            return {'user': self.Env.get('user')}

    @register(Model)
    class Pyramid:

        @classmethod
        def check_user_exists(cls, login):
            return True

        @classmethod
        def check_login(cls, **kwargs):
            return True


@pytest.fixture(scope="class")
def registry_context_with_furetui(request, webserver, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], add_context_with_furetui
    )
    registry.Test.insert(code='test')
    webserver.post_json(
        '/furet-ui/login', {'login': 'test', 'password': 'test'},
        status=200)

    def logout():
        webserver.post_json('/furet-ui/logout', status=200)
        registry.close()

    request.addfinalizer(logout)
    return registry


class TestContextWithFuretUI(Mixin):

    def test_default_context_with_furetui(
        self, webserver, registry_context_with_furetui
    ):
        response = self.call(webserver, 'on_method')
        assert response.json_body == {'user': 'test'}


def add_inherit_context_with_furetui():
    add_context_with_furetui()

    @register(Model)
    class Test:

        def on_method(self, param=None):
            res = super().on_method()
            res['foo'] = 'bar'
            return res


@pytest.fixture(scope="class")
def registry_inherit_context_with_furetui(request, webserver, bloks_loaded):
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], add_inherit_context_with_furetui
    )
    registry.Test.insert(code='test')
    webserver.post_json(
        '/furet-ui/login', {'login': 'test', 'password': 'test'},
        status=200)

    def logout():
        webserver.post_json('/furet-ui/logout', status=200)
        registry.close()

    request.addfinalizer(logout)
    return registry


class TestInheritContextWithFuretUI(Mixin):

    def test_default_context_with_furetui(
        self, webserver, registry_inherit_context_with_furetui
    ):
        response = self.call(webserver, 'on_method')
        assert response.json_body == {'user': 'test', 'foo': 'bar'}


def add_context_with_furetui_and_auth():
    @register(Model)
    class Test:

        code = String(primary_key=True)

        @exposed_method(is_classmethod=False)
        def on_method(self, param=None):
            return {
                'user': self.Env.get('user'),
                'lang': self.Env.get('lang'),
            }


LANGS = ['fr', 'en']


@pytest.fixture(scope="class", params=LANGS)
def registry_context_with_furetui_and_auth(request, webserver, bloks_loaded):
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui", "furetui-auth"], add_context_with_furetui_and_auth
    )
    registry.Pyramid.User.insert(login='test')
    registry.Pyramid.CredentialStore.insert(
       login='test', password='test', lang=request.param)
    registry.Test.insert(code='test')
    webserver.post_json(
        '/furet-ui/login', {'login': 'test', 'password': 'test'},
        status=200)

    def logout():
        webserver.post_json('/furet-ui/logout', status=200)
        registry.close()

    request.addfinalizer(logout)
    return registry


class TestContextWithFuretUIAuth(Mixin):

    def test_default_context_with_furetui(
        self, webserver, registry_context_with_furetui_and_auth
    ):
        response = self.call(webserver, 'on_method')
        user = registry_context_with_furetui_and_auth.Pyramid.User.query(
        ).get('test'),
        assert response.json_body == {
            'user': user,
            'lang': user.lang,
        }


def add_inherit_context_with_furetui_and_auth():
    add_context_with_furetui_and_auth()

    @register(Model)
    class Test:

        def on_method(self, param=None):
            res = super().on_method()
            res['foo'] = 'bar'
            return res


@pytest.fixture(scope="class", params=LANGS)
def registry_inherit_context_with_furetui_and_auth(
    request, webserver, bloks_loaded
):
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui", "furetui-auth"], add_inherit_context_with_furetui_and_auth
    )
    registry.Pyramid.User.insert(login='test')
    registry.Pyramid.CredentialStore.insert(
       login='test', password='test', lang=request.param)
    registry.Test.insert(code='test')
    webserver.post_json(
        '/furet-ui/login', {'login': 'test', 'password': 'test'},
        status=200)

    def logout():
        webserver.post_json('/furet-ui/logout', status=200)
        registry.close()

    request.addfinalizer(logout)
    return registry


class TestInheritContextWithFuretUIAuth(Mixin):

    def test_default_context_with_furetui(
        self, webserver, registry_inherit_context_with_furetui_and_auth
    ):
        response = self.call(webserver, 'on_method')
        user = registry_context_with_furetui_and_auth.Pyramid.User.query(
        ).get('test'),
        assert response.json_body == {
            'user': user,
            'lang': user.lang,
            'foo': 'bar',
        }
