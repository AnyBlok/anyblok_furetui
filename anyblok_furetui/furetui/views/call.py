from anyblok_pyramid import current_blok
from cornice import Service
from anyblok_furetui.security import authorized_furetui_user


call = Service(name='call',
               path='/furet-ui/resource/{resource}/model/{model}/call/{call}',
               description='Generic Call',
               cors_origins=('*',),
               cors_credentials=True,
               installed_blok=current_blok())


@call.post()
@authorized_furetui_user(in_data=False)
def call_classmethod(request):
    registry = request.anyblok.registry
    params = request.matchdict
    body = request.json_body

    return registry.FuretUI.call_exposed_method(request, **params, **body)
