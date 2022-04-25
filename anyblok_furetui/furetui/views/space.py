from anyblok_pyramid import current_blok
from cornice import Service
from anyblok_furetui.security import authorized_furetui_user


space = Service(name='space',
                path='/furet-ui/space/{code}',
                description='Space information',
                cors_origins=('*',),
                cors_credentials=True,
                installed_blok=current_blok())


@space.get()
@authorized_furetui_user(in_data=False)
def get_space(request):
    # check user has access right
    registry = request.anyblok.registry
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
