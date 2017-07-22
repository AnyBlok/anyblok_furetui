from anyblok.blok import Blok
from anyblok_furetui.release import version
from logging import getLogger
logger = getLogger(__name__)


class FuretUIBlok(Blok):
    version = version

    required = [
        'anyblok-core',
    ]

    @classmethod
    def import_declaration_module(cls):
        pass

    @classmethod
    def reload_declaration_module(cls, reload):
        pass
