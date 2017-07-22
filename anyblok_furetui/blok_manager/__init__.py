from anyblok.blok import Blok
from anyblok_furetui.release import version
from logging import getLogger
logger = getLogger(__name__)


class BlokManager(Blok):
    version = version

    required = [
        'furetui',
    ]

    @classmethod
    def import_declaration_module(cls):
        pass

    @classmethod
    def reload_declaration_module(cls, reload):
        pass
