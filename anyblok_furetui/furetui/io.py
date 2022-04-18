# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2020 Pierre Verkest <pierreverkest84@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from logging import getLogger


logger = getLogger(__name__)


@Declarations.register(Declarations.Model.IO)
class Mapping:

    @classmethod
    def set_primary_keys(cls, model, key, pks, raiseifexist=True,
                         blokname=None):
        """ Add or update a mmping with a model and a external key

        :param model: model to check
        :param key: string of the key
        :param pks: dict of the primary key to save
        :param raiseifexist: boolean (True by default), if True and the entry
            exist then an exception is raised
        :param blokname: name of the blok where come from the mapping
        :exception: IOMappingSetException
        """
        mapping = cls.query().filter(
            cls.filter_by_model_and_key(model, key)).one_or_none()
        if mapping:
            if raiseifexist:
                super().set_primary_keys(
                    model, key, pks, raiseifexist=raiseifexist,
                    blokname=blokname)

            if mapping.blokname != blokname:
                return mapping

        return super().set_primary_keys(
            model, key, pks, raiseifexist=raiseifexist, blokname=blokname)
