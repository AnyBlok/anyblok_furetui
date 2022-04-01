from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request
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
    with saved_errors_in_request(request):
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
