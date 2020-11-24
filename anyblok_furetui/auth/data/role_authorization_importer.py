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

    ACCESS_CRUD = dict(
        perms=dict(
            create=dict(
                matched=True,
            ),
            read=dict(
                matched=True,
            ),
            update=dict(
                matched=True,
            ),
            delete=dict(
                matched=True,
            ),
        ),
        extra_authz_params=dict(
            order=100,
        ),
    )
    ACCESS_CRU_ = dict(
        perms=dict(
            create=dict(
                matched=True,
            ),
            read=dict(
                matched=True,
            ),
            update=dict(
                matched=True,
            ),
            delete=dict(
                matched=False,
            ),
        ),
        extra_authz_params=dict(
            order=110,
        ),
    )
    ACCESS_CR_D = dict(
        perms=dict(
            create=dict(
                matched=True,
            ),
            read=dict(
                matched=True,
            ),
            update=dict(
                matched=False,
            ),
            delete=dict(
                matched=True,
            ),
        ),
        extra_authz_params=dict(
            order=120,
        ),
    )
    ACCESS__RUD = dict(
        perms=dict(
            create=dict(
                matched=False,
            ),
            read=dict(
                matched=True,
            ),
            update=dict(
                matched=True,
            ),
            delete=dict(
                matched=True,
            ),
        ),
        extra_authz_params=dict(
            order=130,
        ),
    )
    ACCESS_C_UD = dict(
        perms=dict(
            create=dict(
                matched=True,
            ),
            read=dict(
                matched=False,
            ),
            update=dict(
                matched=True,
            ),
            delete=dict(
                matched=True,
            ),
        ),
        extra_authz_params=dict(
            order=140,
        ),
    )
    ACCESS_CR__ = dict(
        perms=dict(
            create=dict(
                matched=True,
            ),
            read=dict(
                matched=True,
            ),
            update=dict(
                matched=False,
            ),
            delete=dict(
                matched=False,
            ),
        ),
        extra_authz_params=dict(
            order=150,
        ),
    )
    ACCESS__RU_ = dict(
        perms=dict(
            create=dict(
                matched=False,
            ),
            read=dict(
                matched=True,
            ),
            update=dict(
                matched=True,
            ),
            delete=dict(
                matched=False,
            ),
        ),
        extra_authz_params=dict(
            order=160,
        ),
    )
    ACCESS__R_D = dict(
        perms=dict(
            create=dict(
                matched=False,
            ),
            read=dict(
                matched=True,
            ),
            update=dict(
                matched=False,
            ),
            delete=dict(
                matched=True,
            ),
        ),
        extra_authz_params=dict(
            order=170,
        ),
    )
    ACCESS___UD = dict(
        perms=dict(
            create=dict(
                matched=False,
            ),
            read=dict(
                matched=False,
            ),
            update=dict(
                matched=True,
            ),
            delete=dict(
                matched=True,
            ),
        ),
        extra_authz_params=dict(
            order=180,
        ),
    )
    ACCESS_C_U_ = dict(
        perms=dict(
            create=dict(
                matched=True,
            ),
            read=dict(
                matched=False,
            ),
            update=dict(
                matched=True,
            ),
            delete=dict(
                matched=False,
            ),
        ),
        extra_authz_params=dict(
            order=190,
        ),
    )
    ACCESS_C__D = dict(
        perms=dict(
            create=dict(
                matched=True,
            ),
            read=dict(
                matched=False,
            ),
            update=dict(
                matched=False,
            ),
            delete=dict(
                matched=True,
            ),
        ),
        extra_authz_params=dict(
            order=200,
        ),
    )
    ACCESS__R__ = dict(
        perms=dict(
            create=dict(
                matched=False,
            ),
            read=dict(
                matched=True,
            ),
            update=dict(
                matched=False,
            ),
            delete=dict(
                matched=False,
            ),
        ),
        extra_authz_params=dict(
            order=210,
        ),
    )
    ACCESS_C___ = dict(
        perms=dict(
            create=dict(
                matched=True,
            ),
            read=dict(
                matched=False,
            ),
            update=dict(
                matched=False,
            ),
            delete=dict(
                matched=False,
            ),
        ),
        extra_authz_params=dict(
            order=220,
        ),
    )
    ACCESS___U_ = dict(
        perms=dict(
            create=dict(
                matched=False,
            ),
            read=dict(
                matched=False,
            ),
            update=dict(
                matched=True,
            ),
            delete=dict(
                matched=False,
            ),
        ),
        extra_authz_params=dict(
            order=230,
        ),
    )
    ACCESS____D = dict(
        perms=dict(
            create=dict(
                matched=False,
            ),
            read=dict(
                matched=False,
            ),
            update=dict(
                matched=False,
            ),
            delete=dict(
                matched=True,
            ),
        ),
        extra_authz_params=dict(
            order=240,
        ),
    )

    ACCESS_READ = ACCESS__R__
    ACCESS_WRITE = ACCESS_CRUD
    ACCESS_UPDATE = ACCESS__RU_

    @classmethod
    def import_authorization_roles(cls, latest=None):
        cls.registry.Data.Role.ensure_role_exists(
            "admin", "Administrator", cls.get_admin_CRUD_models, latest=latest
        )

    @classmethod
    def get_admin_CRUD_models(cls):
        return {
            "Model.Pyramid.Authorization": cls.ACCESS_WRITE,
            "Model.Pyramid.User": cls.ACCESS_WRITE,
            "Model.Pyramid.Role": cls.ACCESS_WRITE,
            "Model.System.Blok": cls.ACCESS_WRITE,
        }


@Declarations.register(Declarations.Model.Data)
class Role:
    @classmethod
    def ensure_role_exists(cls, name, label, config_callback, latest=None):
        """Create or update Pyramid.Role with related model's authorization

        :param name: str, Role name
        :param label: str, Role label
        :param config_callback: function, A call back that must return a dict
                                of permissions per model::

            {
                "Model.Test": {
                    perms: {
                        "create": {"matched": True},
                        "read": {"matched": True},
                        "update": {"matched": True},
                        "delete": {"matched": True}
                    },
                    extra_authz_params: {
                        "order": 100,
                    }
                }
            }

        :return: Created or updated role

        .. note::

            At the time writting removing existing authorization is not
            managed
        """
        role = cls.registry.Pyramid.Role.query().get(name)
        if not role:
            role = cls.registry.Pyramid.Role.insert(name=name, label=label)
        else:
            role.update(label=label)

        for model, authz in config_callback().items():
            cls.registry.Data.Authorization.ensure_role_model_authorization(
                role, model, authz, latest=latest
            )
        return role


@Declarations.register(Declarations.Model.Data)
class Authorization:

    @classmethod
    def ensure_role_model_authorization(
        cls, role, model, authorizatoions, latest=None
    ):
        if not authorizatoions:
            authorizatoions = {}
        authz = (
            cls.registry.Pyramid.Authorization.query()
            .filter_by(
                role=role,
                model=model,
            )
            .one_or_none()
        )
        if not authz:
            authz = cls.registry.Pyramid.Authorization.insert(
                role=role,
                model=model,
            )
        authz.update(
            perms=authorizatoions.get("perms", {}),
            **authorizatoions.get("extra_authz_params", {})
        )
        authz.flag_modified("perms")
        return authz
