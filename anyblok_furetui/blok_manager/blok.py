from anyblok import Declarations
from anyblok.field import Function
from anyblok.blok import BlokManager
from anyblok.registry import RegistryManager
from docutils.core import publish_programmatically
from docutils import io
from rst2html5_ import HTML5Writer
from os.path import join, isfile
from lxml import html


register = Declarations.register
System = Declarations.Model.System


@Declarations.register(Declarations.Model.System)
class Blok:

    logo = Function(fget='get_logo')

    def _get_logo_for(self):
        return {
            'anyblok-core': {
                'blok': 'furetui',
                'path': 'static/images/logo.png',
            }
        }

    def get_logo_for(self, blok_name):
        entries = self._get_logo_for()
        return entries.get(blok_name)

    def get_logo(self):
        """ Return the logo define in blok description

        ::

            class MyBlok(Blok):
                logo = 'path/to/the/logo/in/blok'

        """
        blok = BlokManager.get(self.name)

        def _get_logo(blok_name, logo_path):
            path = BlokManager.getPath(blok_name)
            file_path = join(path, logo_path)
            if isfile(file_path):
                return self.registry.Web.Image.filepath2html(file_path)
            else:
                return None

        if hasattr(blok, 'logo'):
            return _get_logo(self.name, blok.logo)
        else:
            entry = self.get_logo_for(self.name)
            if entry:
                return _get_logo(entry['blok'], entry['path'])

            return _get_logo('blok_manager', 'static/image/none.png')

    def convert_rst2html(self, rst):
        """Convert a rst to html

        :param rst: rst source
        :rtype: html souce
        """
        output, _ = publish_programmatically(
            source_class=io.StringInput, source=rst, source_path=None,
            destination_class=io.StringOutput, destination=None,
            destination_path=None, reader=None, reader_name='standalone',
            parser=None, parser_name='restructuredtext',
            writer=HTML5Writer(), writer_name='null',
            settings=None, settings_spec=None, settings_overrides={},
            config_section=None, enable_exit_status=None)
        return html.tostring(html.fromstring(output).find('body')).decode('utf-8')

    def get_short_description(self):
        """Overwrite the description to return a html"""
        res = super(Blok, self).get_short_description()
        return self.convert_rst2html(res)

    def convert_path(self, res):
        """Change the path of static image"""
        return res

    def get_long_description(self):
        """Overwrite the description to return a html"""
        res = super(Blok, self).get_long_description()
        res = self.convert_path(res)
        return self.convert_rst2html(res)

    # FIXME install, upgrade and uninstall must:
    # * RELOAD: when furetUI component is Modified
    # * REFRESH: in the other case, just return data
    @classmethod
    def furetui_action_when_blok_states_have_changes(cls, viewId=None,
                                                     entries=None):
        print(' FIX ME : RELOAD OR REFRESH', viewId, entries)
        return [{'type': 'RELOAD'}]

    @classmethod
    def install_blok(cls, entries=None, viewId=None, **kwargs):
        """Hight level method to install one blok"""
        if not entries:
            return []

        cls.registry.upgrade(install=[x.name for x in entries])
        return cls.furetui_action_when_blok_states_have_changes(
            viewId=viewId, entries=entries)

    @classmethod
    def upgrade_blok(cls, entries=None, viewId=None, **kwargs):
        """Hight level method to upgrade one blok"""
        if not entries:
            return []

        cls.registry.upgrade(update=[x.name for x in entries])
        return cls.furetui_action_when_blok_states_have_changes(
            viewId=viewId, entries=entries)

    @classmethod
    def uninstall_blok(cls, entries=None, viewId=None, **kwargs):
        """Hight level method to uninstall one blok"""
        if not entries:
            return []

        bloks = [x.name for x in entries]
        cls.registry.upgrade(uninstall=bloks)
        if 'blok_manager' in bloks:
            return [
                {
                    'type': 'UPDATE_ROUTE',
                    'name': 'homepage',
                },
                {
                    'type': 'RELOAD',
                },
            ]

        return cls.furetui_action_when_blok_states_have_changes(
            viewId=viewId, entries=entries)

    @classmethod
    def reload_blokmanager(cls, **kwargs):
        """Reload all the  bloks with their code sources"""
        RegistryManager.clear()  # close all the registry
        BlokManager.reload()  # reload all the blok code
        # FIXME BlokManager.reload should close all the registry and
        # forbidden load registry during the reload
        return [{'type': 'RELOAD'}]
