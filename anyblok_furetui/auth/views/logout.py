from anyblok_pyramid import current_blok
from cornice import Service
from pyramid.response import Response
from pyramid.security import forget


logout = Service(name='logout_furet_ui',
                 path='/furetui/logout',
                 cors_origins=('*',),
                 installed_blok=current_blok())


@logout.post()
def post_logout(request):
    registry = request.anyblok.registry
    FuretUI = registry.FuretUI
    # Call un authentication on FuretUI
    authenticated_userid = None
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
    return Response(json_body=res, headers=forget(request))
