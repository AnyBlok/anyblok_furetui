import pytest
from anyblok import Declarations
from anyblok.config import get_db_name
from anyblok_furetui import furet_ui_call
from anyblok.column import String
from anyblok.tests.conftest import (  # noqa F401
    init_registry_with_bloks,
    reset_db,
    bloks_loaded,
    base_loaded,
)


register = Declarations.register
Core = Declarations.Core
Mixin = Declarations.Mixin
Model = Declarations.Model


def add_core_in_registry():
    @register(Core)
    class Base:

        @furet_ui_call(is_classmethod=True)
        def on_classmethod(cls, param=None):
            pass

        @furet_ui_call(is_classmethod=False)
        def on_method(self, param=None):
            pass

        @furet_ui_call(request='request')
        def with_request(cls, request, param=None):
            pass

        @furet_ui_call(authenticated_userid='user')
        def with_authenticated_userid(cls, user, param=None):
            pass

        @furet_ui_call(resource='resource')
        def with_resource(cls, resource, param=None):
            pass


def add_mixin_in_registry():

    @register(Mixin)
    class MixinTest:

        @furet_ui_call(is_classmethod=True)
        def on_classmethod(cls, param=None):
            pass

        @furet_ui_call(is_classmethod=False)
        def on_method(self, param=None):
            pass

        @furet_ui_call(request='request')
        def with_request(cls, request, param=None):
            pass

        @furet_ui_call(authenticated_userid='user')
        def with_authenticated_userid(cls, user, param=None):
            pass

        @furet_ui_call(resource='resource')
        def with_resource(cls, resource, param=None):
            pass


def add_model_in_registry():

    @register(Model)
    class Test:

        @furet_ui_call(is_classmethod=True)
        def on_classmethod(cls, param=None):
            return super(cls, Test).on_classmethod(param=param)

        @furet_ui_call(is_classmethod=False)
        def on_method(self, param=None):
            return super(self, Test).on_method(param=param)

        @furet_ui_call(request='request')
        def with_request(cls, request, param=None):
            return super(cls, Test).with_request(request, param=param)

        @furet_ui_call(authenticated_userid='user')
        def with_authenticated_userid(cls, user, param=None):
            return super(cls, Test).with_authenticated_userid(
                user, param=param)

        @furet_ui_call(resource='resource')
        def with_resource(cls, resource, param=None):
            return super(cls, Test).with_resource(resource, param=param)


def _with_call_method(oncore=False, onmixin=False, onmodel=False):

    if oncore:
        add_core_in_registry()

    @register(Mixin)
    class MixinTest:
        pass

    if onmixin:
        add_mixin_in_registry()

    @register(Model)
    class Test(MixinTest):
        code = String(primary_key=True)

        def not_decorated(cls):
            return True  # must be raised

        def on_classmethod(cls, param=None):
            return param

        def on_method(self, param=None):
            return self.id, param

        def with_request(cls, request, param=None):
            return request.anyblok.registry.db_name, param

        def with_authenticated_userid(cls, user, param=None):
            return user, param

        def with_resource(cls, resource, param=None):
            return resource, param

    if onmodel:
        add_model_in_registry()


KWARGS = [
    {'oncore': True},
    {'onmixin': True},
    {'onmodel': True},
    {'oncore': True, 'onmixin': True, 'onmodel': True},
]


@pytest.fixture(scope="class", params=KWARGS)
def registry_call_method(request, webserver, bloks_loaded):  # noqa F811
    reset_db()
    registry = init_registry_with_bloks(
        ["furetui"], _with_call_method,
        **request.param
    )
    registry.Pyramid.User.insert(login='test')
    registry.Pyramid.CredentialStore.insert(
       login='test', password='test')
    webserver.post_json(
        '/furet-ui/login', {'login': 'test', 'password': 'test'},
        status=200)

    def logout():
        webserver.post_json('/furet-ui/logout', status=200)
        registry.close()

    request.addfinalizer(logout)
    return registry


class TestCallMethod:
    @pytest.fixture(autouse=True)
    def transact(self, request, registry_call_method):
        transaction = registry_call_method.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def call(self, webserver, call, status=200):
        url = f'/furet-ui/resource/0/model/Model.Test/call/{call}'
        params = {'data': {'param': 1}, 'pks': {'code': 'test'}}
        webserver.post_json(url, params, status=status)

    def test_undecorated_method(self, webserver, registry_call_method):
        self.call(webserver, 'not_decorated', status=403)

    def test_decorated_classmethod(self, webserver, registry_call_method):
        response = self.call(webserver, 'on_classmethod')
        assert response.data == 1

    def test_decorated_method(self, webserver, registry_call_method):
        registry_call_method.Test.insert(code='test')
        response = self.call(webserver, 'on_method')
        assert response.data == ('test', 1)

    def test_decorated_with_request(self, webserver, registry_call_method):
        response = self.call(webserver, 'with_request')
        assert response.data == (get_db_name(), 1)

    def test_decorated_with_authenticated_user(self, webserver,
                                               registry_call_method):
        response = self.call(webserver, 'with_authenticated_userid')
        assert response.data == ('test', 1)

    def test_decorated_with_resource(self, webserver, registry_call_method):
        response = self.call(webserver, 'with_resource')
        assert response.data == ('0', 1)

    @pytest.mark.skip()
    def test_decorated_with_permission(self, webserver, registry_call_method):
        raise Exception('NotImplemented')
