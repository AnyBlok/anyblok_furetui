from anyblok_pyramid import current_blok
from cornice import Service


resource = Service(name='resource',
                   path='/furet-ui/resource/{id}',
                   description='Resource information',
                   cors_origins=('*',),
                   cors_credentials=True,
                   installed_blok=current_blok())


@resource.get()
def get_resource(request):
    # check user is disconnected
    # check user has access right
    registry = request.anyblok.registry
    resourceId = request.matchdict['id']
    resource = registry.FuretUI.Resource.query().get(resourceId)
    res = []
    if resource:
        res = [
            {
                'type': 'UPDATE_RESOURCES',
                'definitions': resource.get_definitions(),
            },
            {
                'type': 'UPDATE_CURRENT_RIGHT_MENUS',
                'menus': resource.get_menus(),
            },
        ]

    return res
