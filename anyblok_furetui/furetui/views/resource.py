from anyblok_pyramid import current_blok
from cornice import Service
from anyblok_furetui.security import authorized_furetui_user


resource = Service(name='resource',
                   path='/furet-ui/resource/{id}',
                   description='Resource information',
                   cors_origins=('*',),
                   cors_credentials=True,
                   installed_blok=current_blok())


@resource.get()
@authorized_furetui_user(in_data=False)
def get_resource(request):
    registry = request.anyblok.registry
    userId = request.authenticated_userid
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
        ]

    return res


open_resource = Service(
    name='open_resource',
    path='/furet-ui/open/resource/{id}',
    description='Resource information',
    cors_origins=('*',),
    cors_credentials=True,
    installed_blok=current_blok())


def get_resource_from_mapping(registry, name, resource_type):
    types = [resource_type] if resource_type else ['List', 'Custom', 'Form']
    for type_ in types:
        resource_model = 'Model.FuretUI.Resource.%s' % type_
        resource = registry.IO.Mapping.get(resource_model, name)
        if resource:
            return resource

    raise Exception('No resource found %r in (%s)' % (name, ', '.join(types)))


@open_resource.post()
@authorized_furetui_user(in_data=False)
def post_open_resource(request):
    registry = request.anyblok.registry
    userId = request.authenticated_userid
    resourceExternalId = request.matchdict['id']
    body = request.json_body
    resource = get_resource_from_mapping(registry, resourceExternalId,
                                         body.get('resource_type', None))
    params = body['params']
    params['id'] = resource.id
    query = body.get('resource_query', '')
    return [
        {
            'type': 'UPDATE_RESOURCES',
            'definitions': resource.get_definitions(
                authenticated_userid=userId),
        },
        {
            'type': 'UPDATE_ROUTE',
            'name': body['route'],
            'params': params,
            'query': query,
        },
    ]
