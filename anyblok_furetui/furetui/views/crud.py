import json
from copy import deepcopy
from anyblok_pyramid import current_blok
from cornice import Service
from anyblok_furetui.security import authorized_furetui_user


crud = Service(name='crud',
               path='/furet-ui/resource/{resource}/crud',
               description='Generic Crud',
               cors_origins=('*',),
               cors_credentials=True,
               installed_blok=current_blok())


@crud.post()
@authorized_furetui_user()
def crud_create(request):
    registry = request.anyblok.registry
    data = request.json_body
    model = data['model']
    uuid = data['uuid']
    changes = deepcopy(data['changes'])
    obj = registry.FuretUI.CRUD.create(
        model, uuid, changes, request.authenticated_userid)
    return {
        'pks': obj.to_primary_keys(),
    }


@crud.get()
@authorized_furetui_user()
def crud_read(request):
    registry = request.anyblok.registry
    return registry.FuretUI.CRUD.read(request)


@crud.patch()
@authorized_furetui_user()
def crud_update(request):
    registry = request.anyblok.registry
    data = request.json_body
    model = data['model']
    pks = data['pks']
    changes = deepcopy(data['changes'])

    obj = registry.FuretUI.CRUD.update(
        model, pks, changes, request.authenticated_userid)
    # create_or_update(registry, changes, firstmodel=model)
    return {
        'pks': obj.to_primary_keys(),
    }


@crud.delete()
@authorized_furetui_user()
def crud_delete(request):
    registry = request.anyblok.registry
    data = request.params
    model = data['model']
    pks = dict(json.loads(data['pks']))

    registry.FuretUI.CRUD.delete(model, pks, request.authenticated_userid)
    return {
        'pks': pks,
    }
