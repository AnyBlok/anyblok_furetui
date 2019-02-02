from anyblok_pyramid import current_blok
from cornice import Service


login = Service(name='login_furet_ui',
                path='/furetui/login',
                cors_origins=('*',),
                installed_blok=current_blok())


@login.post()
def post_login(request):
    registry = request.anyblok.registry
    FuretUI = registry.FuretUI
    # Call authentication on FuretUI
    authenticated_userid = request.authenticated_userid
    default_spaces_menu = FuretUI.get_default_space(authenticated_userid)
    res = {
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
