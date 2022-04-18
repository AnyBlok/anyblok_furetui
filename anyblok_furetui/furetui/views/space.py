from anyblok_pyramid import current_blok
from cornice import Service
from anyblok_furetui.security import authorized_user


space = Service(name='space',
                path='/furet-ui/space/{code}',
                description='Space information',
                validators=(authorized_user,),
                cors_origins=('*',),
                cors_credentials=True,
                installed_blok=current_blok())


@space.get()
def get_space(request):
    # check user is disconnected
    # check user has access right
    registry = request.anyblok.registry
    try:
        registry = request.anyblok.registry
        code = request.matchdict['code']
        space = registry.FuretUI.Space.query().get(code)
        res = []
        if space:
            res = [
                {
                    'type': 'UPDATE_CURRENT_LEFT_MENUS',
                    'menus': space.get_menus(),
                },
            ]
        return res
    except registry.FuretUI.UserError as e:
        return [e.get_furetui_error()]
    except Exception as e:
        return [
            registry.FuretUI.UnknownError(str(e)).get_furetui_error()
        ]
