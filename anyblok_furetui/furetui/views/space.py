from anyblok_pyramid import current_blok
from cornice import Service


spaces = Service(name='spaces',
                 path='/furet-ui/spaces',
                 description='List spaces',
                 cors_origins=('*',),
                 cors_credentials=True,
                 installed_blok=current_blok())


@spaces.get()
def get_spaces(request):
    # check user is disconnected
    registry = request.anyblok.registry
    Space = registry.FuretUI.Space
    query = Space.get_for_user(request.authenticated_userid)
    res = [{
        'type': 'UPDATE_SPACE_MENUS',
        'menus': [
            {
                'code': x.code,
                'label': x.label,
                'icon': {
                    'code': x.icon_code,
                    'type': x.icon_type,
                },
                'description': x.description,
                'path': x.get_path(),
            }
            for x in query
        ],
    }]
    return res


space = Service(name='space',
                path='/furet-ui/space/{code}',
                description='Space information',
                cors_origins=('*',),
                cors_credentials=True,
                installed_blok=current_blok())


@space.get()
def get_space(request):
    # check user is disconnected
    # check user has access right
    registry = request.anyblok.registry
    code = request.matchdict['code']
    space = registry.FuretUI.Space.query().get(code)
    res = []
    if space:
        res = [
            {
                'type': 'UPDATE_CURRENT_SPACE',
                'label': space.label,
            },
            {
                'type': 'UPDATE_CURRENT_LEFT_MENUS',
                'menus': space.get_menus(),
            },
        ]
    return res
