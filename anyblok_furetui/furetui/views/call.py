from anyblok_pyramid import current_blok
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
    body = request.json_body
    # TODO call security hooks

    res = registry.FuretUI.call_exposed_method(request, **params, **body)
    if res is None:
        return []

    return res
