from pyramid.httpexceptions import HTTPFound
from anyblok.config import Configuration
from anyblok_pyramid import current_blok
from anyblok_pyramid.bloks.auth.views import (
    login as auth_login, logout as auth_logout)
from anyblok.blok import BlokManager
from pyramid.response import FileResponse
from os.path import join
from cornice import Service


client = Service(name='client_furet_ui',
                 path=Configuration.get('furetui_client_path', '/furet-ui'),
                 description='get FuretUI web client',
                 installed_blok=current_blok())


@client.get()
def get_client_file(request):
    blok_path = BlokManager.getPath('furetui')
    path = join(blok_path, 'static', 'index.html')
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
    auth_login(request)
    authenticated_userid = request.json_body['login']
    res = FuretUI.get_user_informations(authenticated_userid)
    redirect = request.json_body.get('redirect', FuretUI.get_default_path(
        authenticated_userid))
    res.append({'type': 'UPDATE_ROUTE', 'path': redirect})
    return res


logout = Service(name='logout_furet_ui',
                 path='/furet-ui/logout',
                 cors_origins=('*',),
                 installed_blok=current_blok())


@logout.post()
def post_logout(request):
    registry = request.anyblok.registry
    FuretUI = registry.FuretUI
    auth_logout(request)
    return FuretUI.get_logout()
