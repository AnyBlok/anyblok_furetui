# This file is a part of the AnyBlok / Pyramid project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request
from anyblok.common import add_autodocs


def authorized_user(request, *a, **kw):
    registry = request.anyblok.registry

    with saved_errors_in_request(request):
        userId = request.authenticated_userid
        if not userId:
            request.errors.add('body', 'userid', 'The user id does not exist')
            request.errors.status = 405

        elif not registry.Pyramid.check_user_exists(userId):
            request.errors.add('body', 'userid', 'The user id does not exist')
            request.errors.status = 405

        if not registry.FuretUI.check_security(request):
            request.errors.add('body', 'userid', 'The user is not allow')
            request.errors.status = 405

        if request.errors.status != 405:
            registry.FuretUI.set_user_context(userId)


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
