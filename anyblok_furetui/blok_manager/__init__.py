# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok_furetui.release import version
from logging import getLogger
logger = getLogger(__name__)


class BlokManager(Blok):
    version = version

    required = [
        'furetui',
    ]

    views = [
        'blok.tmpl',
    ]

    def update(self, latest_version):
        """ Update the database """
        self.import_file('xml', 'Model.Web.Space', 'space.xml')

    def uninstall(self):
        data2remove_by_model = [
            ['Model.UI.Action.Button', [
                "buttons_blok_manager_reload_all_bloks"]],
            ['Model.UI.Action.ButtonGroup', [
                "group_button_blok_manager_other"]],
            ['Model.UI.Action.Transition', [
                "transition_blok_manager_select_record",
                "transition_blok_manager_new_record"]],
            ['Model.UI.View', [
                "view_blok_thumbnails",
                "view_blok_form"]],
            ['Model.Web.Space', ['setting_space_blok']],
            ['Model.UI.Action', ["action_setting_blok"]],
        ]
        Mapping = self.registry.IO.Mapping
        kwargs = {'mapping_only': False}
        for model, keys in data2remove_by_model:
            Mapping.multi_delete(model, *keys, **kwargs)
