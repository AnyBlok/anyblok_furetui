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
from urllib.parse import urlparse
try:
    from anyblok_pyramid.bloks.pyramid import oidc
except ImportError:
    oidc = None


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
    return HTTPFound('/furetui/static/images/logo.png')


init = Service(name='init_furet_ui',
               path='/furet-ui/initialize',
               description='get global data for backend initialization',
               cors_origins=('*',),
               cors_credentials=True,
               installed_blok=current_blok())


@init.get()
def get_global_init(request):
    res = request.anyblok.registry.FuretUI.get_initialize(
        request.authenticated_userid)
    if request.session.get("init_redirect_uri"):
        res.append({'type': 'UPDATE_ROUTE',
                    'path': request.session.get("init_redirect_uri")})
    return res


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


oidc_login = Service(
    name='oidc_login_furet_ui',
    path='/furet-ui/oidc/login',
    installed_blok=current_blok()
)


@oidc_login.post()
def oic_login(request):
    if oidc is None:
        raise ImportError('pyoidc is not installed')

    request.session.update({"redirect": request.json_body.get('redirect')})
    location = oidc.prepare_auth_url(request)
    return location


oidc_callback = Service(
    name='oidc_login_callback_furet_ui',
    path='/furet-ui/oidc/callback',
    installed_blok=current_blok()
)


@oidc_callback.get()
def oic_callback(request):
    if oidc is None:
        raise ImportError('pyoidc is not installed')

    # get redirection before before connection as session is invalidate
    # once user is successfully logged
    redirect = request.session.get("redirect")
    user_info, headers = oidc.log_user(request)
    if headers is None:
        # TODO find a way to display a nice error message to enduser
        # probably using session
        request.errors.add('cookies', 'OpenID connect',
                           'Impossible toconnect to oidc')
        request.errors.add('cookies', 'OpenID connect',
                           str(user_info))
        request.session.update({"init_redirect_uri": 'login'})
    else:
        request.session.update(
            {
                "init_redirect_uri": (
                    redirect if redirect else
                    request.anyblok.registry.FuretUI.get_default_path(
                        request.authenticated_userid)
                ),
            }
        )

    return HTTPFound(
        location=urlparse(
            request.environ.get("HTTP_X_FORWARDED_HOST"),
            scheme=request.environ.get("HTTP_X_FORWARDED_PROTO")
        ).geturl(),
        headers=headers
    )
