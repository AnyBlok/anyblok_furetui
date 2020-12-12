"""Blok declaration example
"""
from anyblok.blok import Blok
from anyblok_io.blok import BlokImporter
from .i18n import en, fr


class FuretUIDeliveryBlok(Blok, BlokImporter):
    """Workshop's Blok class definition
    """
    version = "0.1.0"
    author = "Your name"
    required = [
        'anyblok-core',
        'furetui',
        'delivery',
    ]

    furetui = {
        'i18n': {
            'en': en,
            'fr': fr,
        },
        'templates': [
            'templates/delivery.tmpl',
        ],
    }

    def update(self, latest):
        self.import_file_xml('Model.FuretUI.Resource', 'data', 'resources.xml')
