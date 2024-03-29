# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2022 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import polib
from logging import getLogger

logger = getLogger(__name__)


class Translation:

    translation = {}
    langs = set()

    @classmethod
    def has_lang(cls, lang):
        return True if lang in cls.langs else False

    @classmethod
    def set(cls, lang, poentry):
        cls.langs.add(lang)
        cls.translation[(lang, poentry.msgctxt, poentry.msgid)] = poentry.msgstr

    @classmethod
    def get(cls, lang, context, text):
        res = cls.translation.get((lang, context, text))
        if not res:
            return text

        return res

    @classmethod
    def define(cls, msgctxt, msgid):
        logger.debug('msgctxt : %r, msgid: %r', msgctxt, msgid)
        return polib.POEntry(
            msgctxt=msgctxt,
            msgid=msgid,
            msgstr='',
        )
