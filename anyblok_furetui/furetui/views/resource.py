from pyramid.httpexceptions import HTTPUnauthorized
from anyblok_pyramid import current_blok
from cornice import Service
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request


resource = Service(name='resource',
                   path='/furet-ui/resource/{id}',
                   description='Resource information',
                   cors_origins=('*',),
                   cors_credentials=True,
                   installed_blok=current_blok())


@resource.get()
def get_resource(request):
    with saved_errors_in_request(request):
        userId = request.authenticated_userid
        if not userId:
            raise HTTPUnauthorized(comment='user not log in')

        registry = request.anyblok.registry

        registry.Pyramid.check_user_exists(userId)
        resourceId = request.matchdict['id']
        resource = registry.FuretUI.Resource.query().get(resourceId)
        res = []
        if resource:
            res = [
                {
                    'type': 'UPDATE_RESOURCES',
                    'definitions': resource.get_definitions(userId),
                },
                {
                    'type': 'UPDATE_CURRENT_RIGHT_MENUS',
                    'menus': resource.get_menus(),
                },
            ]

        return res
