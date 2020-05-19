from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request
from cornice import Service
from anyblok_furetui.security import authorized_user


call = Service(name='call',
               path='/furet-ui/resource/{resource}/model/{model}/call/{call}',
               description='Generic Call',
               validators=(authorized_user,),
               cors_origins=('*',),
               cors_credentials=True,
               installed_blok=current_blok())


@call.post()
def call_classmethod(request):
    registry = request.anyblok.registry
    params = request.matchdict
    data = request.json_body
    # TODO call security hooks

    with saved_errors_in_request(request):
        Model = registry.get(params['model'])
        res = getattr(Model, params['call'])(**data)
        if res is None:
            return []

        return res
