# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok_furetui.release import version
from logging import getLogger
from .i18n import fr, en

logger = getLogger(__name__)


class FuretUIBlok(Blok):
    """Setup FuretUI for AnyBlok"""
    version = version
    author = 'Suzanne Jean-Sébastien'
    logo = 'static/images/logo.png'

    required = [
        'anyblok-core',
        'auth-password',
    ]

    furetui = {
        'i18n': {
            'en': en,
            'fr': fr,
        },
        'views': [
        ],
    }

    def load(self):
        self.registry.FuretUI.pre_load()

    @classmethod
    def import_declaration_module(cls):
        from . import furetui  # noqa
        from . import space  # noqa
        # from . import menus  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import furetui
        reload(furetui)
        from . import space
        reload(space)
        # from . import menus
        # reload(menus)

    @classmethod
    def pyramid_load_config(cls, config):
        config.scan(cls.__module__ + '.views')
