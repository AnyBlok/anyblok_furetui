# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2020 Pierre Verkest <pierreverkest84@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations


@Declarations.register(Declarations.Model)
class Data:
    """Namespace with helpers to import data
    
    All methods should be idempotent and called at update times
    """
    
    @classmethod
    def import_authorization_roles(cls, latest=None):
        cls.registry.Data.Role.ensure_admin_role_exists(latest=latest)


@Declarations.register(Declarations.Model.Data)
class Role:

    @classmethod
    def ensure_admin_role_exists(cls, latest=None):
        admin = cls.registry.Pyramid.Role.query().get("admin")
        label = "Administrator"
        if not admin:
            admin = cls.registry.Pyramid.Role.insert(
                name="admin",
                label=label
            )
        else:
            admin.update(label=label)

        cls.registry.Data.Authorization.ensure_role_model_authorization_exists(
            admin, "Model.Pyramid.User", latest=latest
        )
        cls.registry.Data.Authorization.ensure_role_model_authorization_exists(
            admin, "Model.Pyramid.Role", latest=latest
        )
        cls.registry.Data.Authorization.ensure_role_model_authorization_exists(
            admin, "Model.System.Blok", latest=latest
        )
    

@Declarations.register(Declarations.Model.Data)
class Authorization:

    @classmethod
    def ensure_role_model_authorization_exists(
        cls, role, model, create=True, read=True, update=True,
        delete=True, order=100, latest=None
    ):
        authz = cls.registry.Pyramid.Authorization.query().filter_by(
            role=role,
            model=model,
        ).one_or_none()
        if not authz:
            authz = cls.registry.Pyramid.Authorization.insert(
                role=role,
                model=model,
            )
        authz.update(
            perm_create=dict(matched=create, ),
            perm_read=dict(matched=read, ),
            perm_update=dict(matched=update, ),
            perm_delete=dict(matched=delete, ),
            order=order,
        )
        authz.flag_modified("perms")
