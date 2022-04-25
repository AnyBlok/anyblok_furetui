# This file is a part of the AnyBlok / Pyramid project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.common import add_autodocs


def authorized_furetui_user(in_data=True):
    error = []
    return_error = {'data': error} if in_data else error
    empty_response = {'data': error} if in_data else error

    def wrap_funct(funct):

        def wrap_call(request):
            registry = request.anyblok.registry
            userId = request.authenticated_userid
            try:
                if not userId:
                    raise registry.FuretUI.ExpiredSession()

                if not registry.Pyramid.check_user_exists(userId):
                    # ADD GO TO login
                    raise registry.FuretUI.UserNotFoundError(
                        message="The user does not exist")

                if not registry.FuretUI.check_security(request):
                    raise registry.FuretUI.UserError(
                        message="The user is not allow to get this resource")

                registry.FuretUI.set_user_context(userId)
                res = funct(request)
                if res is None:
                    return empty_response

                return res
            except registry.FuretUI.UserError as e:
                error.append(e.get_furetui_error())
            except Exception as e:
                error.append(
                    registry.FuretUI.UnknownError(str(e)).get_furetui_error()
                )
            return return_error

        return wrap_call

    return wrap_funct


def exposed_method(**kwargs):
    """Decorator to expose a method from the api

    The goal is to forbid the call on a method which is not exposed

    ::

        from anyblok_furetui import exposed_method

        @register(Model)
        class MyModel:

            @exposed_method()
            def to_something(**kwargs):
                do something
                return result or not

    the decorator have some parameters

    :param is_classmethod: bool, defined if the method is a classmethod or not
                           (default: True)
    :param request: str, added request in the decorated method arguments under
                    the str name, if None the request is not added
                    (default None)
    :param authenticated_userid: str, added authenticated_userid in the
                    decorated method arguments under the str name, if None the
                    authenticated_userid is not added (default None)
    :param resource: str, added resource in the decorated method arguments
                     under the str name, if None the resource is not added
                     (default None)
    :param permission: str, verify if the authenticated_userid is allowed to
                       call the method, if None all user are allowed
                       (default None)
    """
    exposed_kwargs = dict(
        is_classmethod=True, permission=None, request=None,
        authenticated_userid=None, resource=None)
    exposed_kwargs.update(kwargs)
    autodoc = "**exposed_method** defined with the arguments {exposed_kwargs:r}"

    def wrapper(method):
        add_autodocs(method, autodoc)
        method.is_an_exposed_method = True
        method.exposure_description = exposed_kwargs
        if exposed_kwargs['is_classmethod'] is True:
            return classmethod(method)

        return method

    return wrapper
