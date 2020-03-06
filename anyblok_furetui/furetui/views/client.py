from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPUnauthorized
from anyblok.config import Configuration
from anyblok_pyramid import current_blok
from anyblok.blok import BlokManager
from pyramid.response import FileResponse
from os.path import join
from cornice import Service
from logging import getLogger


logger = getLogger(__name__)


client = Service(name='client_furet_ui',
                 path=Configuration.get('furetui_client_path', '/furet-ui'),
                 description='get FuretUI web client',
                 installed_blok=current_blok())


@client.get()
def get_client_file(request):
    blok_name, static_path = Configuration.get('furetui_client_static',
                                               'furetui:static').split(':')
    blok_path = BlokManager.getPath(blok_name)
    path = join(blok_path, *static_path.split('/'), 'index.html')
    return FileResponse(path, request=request, content_type='text/html')


logo = Service(name='logo',
               path='/furet-ui/logo',
               description='Redirect to static logo',
               cors_origins=('*',),
               installed_blok=current_blok())


@logo.get()
def get_logo(request):
    return HTTPFound('/furetui/static/logo.png')


init = Service(name='init_furet_ui',
               path='/furet-ui/initialize',
               description='get global data for backend initialization',
               cors_origins=('*',),
               cors_credentials=True,
               installed_blok=current_blok())


@init.get()
def get_global_init(request):
    return request.anyblok.registry.FuretUI.get_initialize(
        request.authenticated_userid)


login = Service(name='login_furet_ui',
                path='/furet-ui/login',
                cors_origins=('*',),
                installed_blok=current_blok())


@login.post()
def post_login(request):
    registry = request.anyblok.registry
    FuretUI = registry.FuretUI

    Pyramid = registry.Pyramid
    params = Pyramid.format_login_params(request)
    login = params['login']
    try:
        Pyramid.check_user_exists(login)
    except Exception as e:
        logger.info('Fail check_user_exists: %r', e)
        registry.rollback()
        request.errors.add('header', 'login', 'wrong username')
        request.errors.status = 401
        return

    try:
        Pyramid.check_login(**params)
        headers = remember(request, login)
        authenticated_userid = request.authenticated_userid
        res = FuretUI.get_user_informations(authenticated_userid)
        redirect = request.json_body.get('redirect', FuretUI.get_default_path(
            authenticated_userid))
        res.append({'type': 'UPDATE_ROUTE', 'path': redirect})
        return Response(json_body=res, headers=headers)
    except HTTPUnauthorized:
        registry.rollback()
        request.errors.add('header', 'password', 'wrong password')
        request.errors.status = 401
        return


logout = Service(name='logout_furet_ui',
                 path='/furet-ui/logout',
                 cors_origins=('*',),
                 installed_blok=current_blok())


@logout.post()
def post_logout(request):
    registry = request.anyblok.registry
    FuretUI = registry.FuretUI
    return Response(json_body=FuretUI.get_logout(), headers=forget(request))
