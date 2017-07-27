from anyblok.declarations import Declarations
from anyblok import reload_module_if_blok_is_reloading
from anyblok.blok import BlokManager


@Declarations.register(Declarations.Model)
class Web:

    @classmethod
    def format_static(cls, blok, static_url):
        """ Replace the attribute #BLOK by the real name of the blok """
        if static_url.startswith('#BLOK'):
            return '/' + blok + static_url[5:]
        else:
            return static_url

    @classmethod
    def get_static(cls, static_type):
        """ return the list of all static file path

        :param static_type: entry in the blok
        :rtype: list of the path
        """
        res = []
        Blok = cls.registry.System.Blok
        for blok in Blok.list_by_state('installed'):
            b = BlokManager.get(blok)
            if hasattr(b, static_type):
                for static_url in getattr(b, static_type):
                    res.append(cls.format_static(blok, static_url))

        return res

    @classmethod
    def get_css(cls):
        """ Return the css paths """
        return cls.get_static('css')

    @classmethod
    def get_js(cls):
        """ return the js paths """
        return cls.get_static('js')

from . import space  # noqa
reload_module_if_blok_is_reloading(space)
from . import action  # noqa
reload_module_if_blok_is_reloading(action)
from . import menu  # noqa
reload_module_if_blok_is_reloading(menu)
from . import view  # noqa
reload_module_if_blok_is_reloading(view)
from . import button  # noqa
reload_module_if_blok_is_reloading(button)
from . import image  # noqa
reload_module_if_blok_is_reloading(image)
