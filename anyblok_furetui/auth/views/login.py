from anyblok_pyramid import current_blok
from cornice import Service
from pyramid.response import Response
from pyramid.security import remember
from pyramid.httpexceptions import HTTPUnauthorized


login = Service(name='login_furet_ui',
                path='/furetui/login',
                cors_origins=('*',),
                installed_blok=current_blok())


@login.post()
def post_login(request):
    User = request.anyblok.registry.User
    params = request.json_body
    login = params['login']
    user = User.query().get(login)
    if not user:
        request.errors.add('header', 'username', 'wrong username')
        request.errors.status = 401
        return

    try:
        User.check_login(**params)
        headers = remember(request, login)

        registry = request.anyblok.registry
        FuretUI = registry.FuretUI
        authenticated_userid = request.authenticated_userid
        default_spaces_menu = FuretUI.get_default_space(authenticated_userid)
        return Response(
            json_body={
                'global': FuretUI.get_global(authenticated_userid),
                'menus': {
                    'user': FuretUI.get_user_menu(authenticated_userid),
                    'spaces': FuretUI.get_spaces_menu(authenticated_userid,
                                                      default_spaces_menu),
                    'spaceMenus': FuretUI.get_space_menus(authenticated_userid,
                                                          default_spaces_menu),
                },
            },
            headers=headers
        )
    except HTTPUnauthorized:
        request.errors.add('header', 'password', 'wrong password')
        request.errors.status = 401
        return
