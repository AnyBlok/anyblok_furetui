# from pyramid.httpexceptions import HTTPFound
from anyblok.config import Configuration
from anyblok_pyramid import current_blok
from pyramid.response import Response
from os.path import join
from cornice import Service
from jinja2 import Template
import pkg_resources


INDEX_CONTENT = pkg_resources.resource_string(
    "anyblok_furetui", join("furetui", "views", "index.jinja"))


client = Service(name='client_furet_ui',
                 path=Configuration.get('furetui_client_path', '/furet-ui'),
                 description='get FuretUI web client',
                 installed_blok=current_blok())


@client.get()
def get_client_file(request):
    registry = request.anyblok.registry
    FuretUI = registry.FuretUI
    res = Template(INDEX_CONTENT.decode("utf-8")).render(
        stylesheets=FuretUI.get_css_files(),
        scripts=FuretUI.get_js_files(),
        templates=FuretUI.get_templates(),
        components=FuretUI.get_component_files(),
        theme=Configuration.get('furetui_ui_theme_path', None),
        debug_level=0
    )
    return Response(res, content_type='text/html')


# init = Service(name='init_furet_ui',
#                path='/furet-ui/app/component/files',
#                description='get global data for backend initialization',
#                cors_origins=('*',),
#                installed_blok=current_blok())
#
#
# @init.get()
# def get_global_init(request):
#     # TODO call cached pre_load
#     registry = request.anyblok.registry
#     FuretUI = registry.FuretUI
#     authenticated_userid = request.authenticated_userid
#     default_spaces_menu = FuretUI.get_default_space(authenticated_userid)
#     res = {
#         'templates': FuretUI.get_templates(),
#         'js': FuretUI.get_js_files(),
#         'css': FuretUI.get_css_files(),
#         'global': FuretUI.get_global(authenticated_userid),
#         'menus': {
#             'user': FuretUI.get_user_menu(authenticated_userid),
#             'spaces': FuretUI.get_spaces_menu(authenticated_userid,
#                                               default_spaces_menu),
#             'spaceMenus': FuretUI.get_space_menus(authenticated_userid,
#                                                   default_spaces_menu),
#         },
#     }
#     return res
#
#
# static = Service(name='furet_ui_js_file',
#                  path='/furet-ui/{blok_name}/{filetype}/{file_path:.*}',
#                  installed_blok=current_blok())
#
#
# @static.get()
# def get_static_file(request):
#     blok_name = request.matchdict['blok_name']
#     file_path = request.matchdict['file_path']
#     blok_path = BlokManager.getPath(blok_name)
#     path = join(blok_path, file_path)
#     content_type = 'text/html'
#     if request.matchdict['filetype'] == 'js':
#         content_type = 'application/javascript'
#     elif request.matchdict['filetype'] == 'css':
#         content_type = 'text/css'
#
#     response = FileResponse(path, request=request, content_type=content_type)
#     response.headerlist.append(('Access-Control-Allow-Origin', '*'))
#     return response
#
#
# login = Service(name='login_furet_ui',
#                 path='/furetui/login',
#                 cors_origins=('*',),
#                 installed_blok=current_blok())
#
#
# @login.post()
# def post_login(request):
#     registry = request.anyblok.registry
#     FuretUI = registry.FuretUI
#     # Call authentication on FuretUI
#     authenticated_userid = request.authenticated_userid
#     default_spaces_menu = FuretUI.get_default_space(authenticated_userid)
#     res = {
#         'global': FuretUI.get_global(authenticated_userid),
#         'menus': {
#             'user': FuretUI.get_user_menu(authenticated_userid),
#             'spaces': FuretUI.get_spaces_menu(authenticated_userid,
#                                               default_spaces_menu),
#             'spaceMenus': FuretUI.get_space_menus(authenticated_userid,
#                                                   default_spaces_menu),
#         },
#     }
#     return res
#
#
# logo = Service(name='logo',
#                path='/furet-ui/logo',
#                description='Redirect to static logo',
#                cors_origins=('*',),
#                installed_blok=current_blok())
#
#
# @logo.get()
# def get_logo(request):
#     return HTTPFound('/furetui/static/logo.png')
#
#
# logout = Service(name='logout_furet_ui',
#                  path='/furetui/logout',
#                  cors_origins=('*',),
#                  installed_blok=current_blok())
#
#
# @logout.post()
# def post_logout(request):
#     registry = request.anyblok.registry
#     FuretUI = registry.FuretUI
#     # Call un authentication on FuretUI
#     authenticated_userid = request.authenticated_userid
#     default_spaces_menu = FuretUI.get_default_space(authenticated_userid)
#     res = {
#         'global': FuretUI.get_global(authenticated_userid),
#         'menus': {
#             'user': FuretUI.get_user_menu(authenticated_userid),
#             'spaces': FuretUI.get_spaces_menu(authenticated_userid,
#                                               default_spaces_menu),
#             'spaceMenus': FuretUI.get_space_menus(authenticated_userid,
#                                                   default_spaces_menu),
#         },
#     }
#     return res
