# This file is a part of the AnyBlok / Pyramid project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request


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


def furet_ui_call(is_classmethod=True, request=None, authenticated_userid=None,
                  resource=None):

    def wrapper(func):
        return func

    return wrapper
