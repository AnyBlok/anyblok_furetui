"""Blok declaration example
"""
from anyblok.blok import Blok
from anyblok_io.blok import BlokImporter
from .i18n import en, fr


class FuretUIAddressBlok(Blok, BlokImporter):
    """Workshop's Blok class definition
    """
    version = "0.1.0"
    author = "Your name"
    required = [
        'anyblok-core',
        'furetui',
        'address',
    ]

    furetui = {
        'i18n': {
            'en': en,
            'fr': fr,
        },
        'templates': [
            'templates/address.tmpl',
        ],
    }

    def update(self, latest):
        self.import_file_xml(
            'Model.FuretUI.Resource', 'data', 'resources.xml')
