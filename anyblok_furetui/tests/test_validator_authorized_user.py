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

    @pytest.fixture(autouse=True)
    def transact(self, request, clear_context):
        return

    def call(self, webserver, call, status=200):
        url = f'/furet-ui/resource/0/model/Model.Test/call/{call}'
        params = {'data': {'param': 1}, 'pks': {'code': 'test'}}
        return webserver.post_json(url, params, status=status)


def add_context():
    @register(Model)
    class Test:

        code = String(primary_key=True)

        def return_context(self):
            context = self.context.copy()
            if 'user' in context:
                context['user'] = context['user'].login

            return context

        @exposed_method(is_classmethod=False)
        def on_method(self, param=None):
            return self.return_context()

        @exposed_method(is_classmethod=False)
        def on_method2(self, param=None):
            with self.context.set(userid='foo'):
                return self.return_context()


def add_inherit_context():

    @register(Model)
    class FuretUI:

        @classmethod
        def set_user_context(self, userId):
            super().set_user_context(userId)
            self.context.set(foo='bar')


def add_context_with_furetui():
    add_context()

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

    def test_set_user_context(
        self, webserver, registry_context_with_furetui
    ):
        response = self.call(webserver, 'on_method')
        assert response.json_body == {'userid': 'test'}

    def test_context_set(
        self, webserver, registry_context_with_furetui
    ):
        response = self.call(webserver, 'on_method2')
        assert response.json_body == {'userid': 'foo'}


def add_inherit_context_with_furetui():
    add_context_with_furetui()
    add_inherit_context()


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

    def test_set_user_context(
        self, webserver, registry_inherit_context_with_furetui
    ):
        response = self.call(webserver, 'on_method')
        assert response.json_body == {'userid': 'test', 'foo': 'bar'}

    def test_context_set(
        self, webserver, registry_inherit_context_with_furetui
    ):
        response = self.call(webserver, 'on_method2')
        assert response.json_body == {'userid': 'foo', 'foo': 'bar'}


LANGS = ['fr', 'en']


@pytest.fixture(scope="class", params=LANGS)
def registry_context_with_furetui_and_auth(request, webserver, bloks_loaded):
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui", "furetui-auth"], add_context
    )
    registry.Pyramid.User.insert(login='test', lang=request.param)
    registry.Pyramid.CredentialStore.insert(
       login='test', password='test')
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

    def test_set_user_context(
        self, webserver, registry_context_with_furetui_and_auth
    ):
        response = self.call(webserver, 'on_method')
        user = registry_context_with_furetui_and_auth.Pyramid.User.query(
        ).get('test')
        assert response.json_body == {
            'userid': user.login,
            'user': user.login,
            'lang': user.lang,
        }

    def test_context_set(
        self, webserver, registry_context_with_furetui_and_auth
    ):
        response = self.call(webserver, 'on_method2')
        user = registry_context_with_furetui_and_auth.Pyramid.User.query(
        ).get('test')
        assert response.json_body == {
            'userid': 'foo',
            'user': user.login,
            'lang': user.lang,
        }


@pytest.fixture(scope="class", params=LANGS)
def registry_inherit_context_with_furetui_and_auth(
    request, webserver, bloks_loaded
):
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui", "furetui-auth"], add_inherit_context_with_furetui
    )
    registry.Pyramid.User.insert(login='test', lang=request.param)
    registry.Pyramid.CredentialStore.insert(
       login='test', password='test')
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

    def test_set_user_context(
        self, webserver, registry_inherit_context_with_furetui_and_auth
    ):
        response = self.call(webserver, 'on_method')
        user = (
            registry_inherit_context_with_furetui_and_auth.Pyramid.User.query(
            ).get('test'))
        assert response.json_body == {
            'userid': user.login,
            'user': user.login,
            'lang': user.lang,
            'foo': 'bar',
        }
