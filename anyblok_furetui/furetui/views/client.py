from pyramid.httpexceptions import HTTPFound
from anyblok.config import Configuration
from anyblok_pyramid import current_blok
from anyblok.blok import BlokManager
from pyramid.response import FileResponse
from os.path import join
from cornice import Service
from pyjsparser import PyJsParser
from logging import getLogger


logger = getLogger(__name__)


client = Service(name='client_furet_ui',
                 path=Configuration.get('furetui_client_path', '/furet-ui'),
                 description='get FuretUI web client',
                 installed_blok=current_blok())


@client.get()
def get_client_file(request):
    print('get_client_file', request.query_string)
    blok_path = BlokManager.getPath('furetui')
    path = join(blok_path, 'static', 'index.html')
    return FileResponse(path, request=request, content_type='text/html')


init = Service(name='init_furet_ui',
               path='/furet-ui/app/component/files',
               description='get global data for backend initialization',
               cors_origins=('*',),
               installed_blok=current_blok())


@init.get()
def get_global_init(request):
    # TODO call cached pre_load
    print('get_global_init', request.query_string)
    registry = request.anyblok.registry
    FuretUI = registry.FuretUI
    if eval(Configuration.get('furetui_debug', False), {}, {}) is True:
        FuretUI.pre_load()

    authenticated_userid = request.authenticated_userid
    default_spaces_menu = FuretUI.get_default_space(authenticated_userid)
    res = {
        'templates': FuretUI.get_templates(),
        'lang': 'fr',
        'langs': FuretUI.get_i18n(),
        'js': FuretUI.get_js_files(),
        'css': FuretUI.get_css_files(),
        'global': FuretUI.get_global(authenticated_userid),
        'menus': {
            'user': FuretUI.get_user_menu(authenticated_userid),
            'spaces': FuretUI.get_spaces_menu(authenticated_userid,
                                              default_spaces_menu),
            'spaceMenus': FuretUI.get_space_menus(authenticated_userid,
                                                  default_spaces_menu),
        },
    }
    return res


static = Service(name='furet_ui_js_file',
                 path='/furet-ui/{blok_name}/{filetype}/{file_path:.*}',
                 installed_blok=current_blok())


class MyPyJsParser(PyJsParser):

    def __init__(self, *args, **kwargs):
        super(MyPyJsParser, self).__init__(*args, **kwargs)
        self.exceptions = {}

    def throwUnexpectedToken(self, token={}, message=''):
        msg = str(self.unexpectedTokenError(token, message))
        msg += '\n' + '\n'.join(self.source.split(
            '\n')[token['lineNumber'] - 3: token['lineNumber']])
        self.exceptions.setdefault(token['lineNumber'], msg)

    def parse(self, blok_name, file_path, content):
        try:
            super(MyPyJsParser, self).parse(content)
        except Exception:
            pass

        for exception in self.exceptions.values():
            logger.error("Parsing error for %s:%r => %s",
                         blok_name, file_path, exception)


@static.get()
def get_static_file(request):
    blok_name = request.matchdict['blok_name']
    file_path = request.matchdict['file_path']
    blok_path = BlokManager.getPath(blok_name)
    path = join(blok_path, file_path)
    content_type = 'text/html'
    if request.matchdict['filetype'] == 'js':
        content_type = 'application/javascript'
        if eval(Configuration.get('furetui_debug', False), {}, {}) is True:
            parser = MyPyJsParser()
            with open(path, 'r') as fp:
                content = fp.read()
                parser.parse(blok_name, file_path, content)

    elif request.matchdict['filetype'] == 'css':
        content_type = 'text/css'

    response = FileResponse(path, request=request, content_type=content_type)
    response.headerlist.append(('Access-Control-Allow-Origin', '*'))
    return response


logo = Service(name='logo',
               path='/furet-ui/logo',
               description='Redirect to static logo',
               cors_origins=('*',),
               installed_blok=current_blok())


@logo.get()
def get_logo(request):
    return HTTPFound('/furetui/static/logo.png')
