import pytest
from anyblok import Declarations
from anyblok.config import get_db_name
from anyblok_furetui import exposed_method
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

        @exposed_method(is_classmethod=True)
        def on_classmethod(cls, param=None):
            pass

        @exposed_method(is_classmethod=False)
        def on_method(self, param=None):
            pass

        @exposed_method(request=True)
        def with_request(cls, request=None, param=None):
            pass

        @exposed_method(request='request2')
        def with_request2(cls, request2=None, param=None):
            pass

        @exposed_method(authenticated_userid=True)
        def with_authenticated_userid(cls, authenticated_userid=None,
                                      param=None):
            pass

        @exposed_method(authenticated_userid='user')
        def with_authenticated_userid2(cls, user=None, param=None):
            pass

        @exposed_method(resource=True)
        def with_resource(cls, resource=None, param=None):
            pass

        @exposed_method(resource='resource2')
        def with_resource2(cls, resource2=None, param=None):
            pass


def add_mixin_in_registry():

    @register(Mixin)
    class MixinTest:

        @exposed_method(is_classmethod=True)
        def on_classmethod(cls, param=None):
            pass

        @exposed_method(is_classmethod=False)
        def on_method(self, param=None):
            pass

        @exposed_method(request=True)
        def with_request(cls, request=None, param=None):
            pass

        @exposed_method(request='request2')
        def with_request2(cls, request2=None, param=None):
            pass

        @exposed_method(authenticated_userid=True)
        def with_authenticated_userid(cls, authenticated_userid=None,
                                      param=None):
            pass

        @exposed_method(authenticated_userid='user')
        def with_authenticated_userid2(cls, user=None, param=None):
            pass

        @exposed_method(resource=True)
        def with_resource(cls, resource=None, param=None):
            pass

        @exposed_method(resource='resource2')
        def with_resource2(cls, resource2=None, param=None):
            pass


def add_model_in_registry(MixinTest):
    @register(Model)
    class Test(MixinTest):
        code = String(primary_key=True)

        def not_decorated(cls):
            return True  # must be raised

        @classmethod
        def on_classmethod(cls, param=None):
            return param

        def on_method(self, param=None):
            return self.code, param

        @classmethod
        def with_request(cls, request=None, param=None):
            return request.anyblok.registry.db_name, param

        @classmethod
        def with_request2(cls, request2=None, param=None):
            return request2.anyblok.registry.db_name, param

        @classmethod
        def with_authenticated_userid(cls, authenticated_userid=None,
                                      param=None):
            return authenticated_userid, param

        @classmethod
        def with_authenticated_userid2(cls, user, param=None):
            return user, param

        @classmethod
        def with_resource(cls, resource, param=None):
            return resource.id if resource else resource, param

        @classmethod
        def with_resource2(cls, resource2, param=None):
            return resource2.id, param


def add_model_with_decorator_in_registry():
    @register(Model)
    class Test:

        @exposed_method(is_classmethod=True)
        def on_classmethod(cls, param=None):
            return super(Test, cls).on_classmethod(param=param)

        @exposed_method(is_classmethod=False)
        def on_method(self, param=None):
            return super(Test, self).on_method(param=param)

        @exposed_method(request=True)
        def with_request(cls, request=None, param=None):
            return super(Test, cls).with_request(
                request=request, param=param)

        @exposed_method(request='request2')
        def with_request2(cls, request2=None, param=None):
            return super(Test, cls).with_request2(
                request2=request2, param=param)

        @exposed_method(authenticated_userid=True)
        def with_authenticated_userid(cls, authenticated_userid=None,
                                      param=None):
            return super(Test, cls).with_authenticated_userid(
                authenticated_userid=authenticated_userid, param=param)

        @exposed_method(authenticated_userid='user')
        def with_authenticated_userid2(cls, user=None, param=None):
            return super(Test, cls).with_authenticated_userid2(
                user=user, param=param)

        @exposed_method(resource=True)
        def with_resource(cls, resource=None, param=None):
            return super(Test, cls).with_resource(
                resource=resource, param=param)

        @exposed_method(resource='resource2')
        def with_resource2(cls, resource2=None, param=None):
            return super(Test, cls).with_resource2(
                resource2=resource2, param=param)


def _with_call_method(oncore=False, onmixin=False, onmodel=False):

    if oncore:
        add_core_in_registry()

    @register(Mixin)
    class MixinTest:
        pass

    if onmixin:
        add_mixin_in_registry()

    add_model_in_registry(MixinTest)

    if onmodel:
        add_model_with_decorator_in_registry()


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
        return webserver.post_json(url, params, status=status)

    def test_undecorated_method(self, webserver, registry_call_method):
        self.call(webserver, 'not_decorated', status=401)

    def test_decorated_classmethod(self, webserver, registry_call_method):
        response = self.call(webserver, 'on_classmethod')
        assert response.json_body == 1

    def test_decorated_method(self, webserver, registry_call_method):
        registry_call_method.Test.insert(code='test')
        response = self.call(webserver, 'on_method')
        assert response.json_body == ['test', 1]

    def test_decorated_with_request(self, webserver, registry_call_method):
        response = self.call(webserver, 'with_request')
        assert response.json_body == [get_db_name(), 1]

    def test_decorated_with_request2(self, webserver, registry_call_method):
        response = self.call(webserver, 'with_request2')
        assert response.json_body == [get_db_name(), 1]

    def test_decorated_with_authenticated_user(self, webserver,
                                               registry_call_method):
        response = self.call(webserver, 'with_authenticated_userid')
        assert response.json_body == ['test', 1]

    def test_decorated_with_authenticated_user2(self, webserver,
                                                registry_call_method):
        response = self.call(webserver, 'with_authenticated_userid2')
        assert response.json_body == ['test', 1]

    def call_with_resource(self, registry, webserver, call):
        resource = registry.FuretUI.Resource.Custom.insert(component='test')
        url = f'/furet-ui/resource/{resource.id}/model/Model.Test/call/{call}'
        params = {'data': {'param': 1}, 'pks': {'code': 'test'}}
        response = webserver.post_json(url, params)
        assert response.json_body == [resource.id, 1]

    def test_decorated_with_resource(self, webserver, registry_call_method):
        self.call_with_resource(
            registry_call_method, webserver, 'with_resource')

    def test_decorated_with_resource_is_0(self, webserver,
                                          registry_call_method):
        response = self.call(webserver, 'with_resource')
        assert response.json_body == [None, 1]

    def test_decorated_with_resource2(self, webserver, registry_call_method):
        self.call_with_resource(
            registry_call_method, webserver, 'with_resource2')

    @pytest.mark.skip()
    def test_decorated_with_permission(self, webserver, registry_call_method):
        raise Exception('NotImplemented')
