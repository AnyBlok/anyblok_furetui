from anyblok_pyramid import current_blok
from cornice import Service
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request
from anyblok_furetui.security import authorized_user


resource = Service(name='resource',
                   path='/furet-ui/resource/{id}',
                   description='Resource information',
                   validators=(authorized_user,),
                   cors_origins=('*',),
                   cors_credentials=True,
                   installed_blok=current_blok())


@resource.get()
def get_resource(request):
    with saved_errors_in_request(request):
        userId = request.authenticated_userid
        registry = request.anyblok.registry
        resourceId = request.matchdict['id']
        resource = registry.FuretUI.Resource.query().get(resourceId)
        res = []
        if resource:
            res = [
                {
                    'type': 'UPDATE_RESOURCES',
                    'definitions': resource.get_definitions(
                        authenticated_userid=userId),
                },
                {
                    'type': 'UPDATE_CURRENT_RIGHT_MENUS',
                    'menus': resource.get_menus(),
                },
            ]

        return res
