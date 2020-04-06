import json
from copy import deepcopy
from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.crud_resource import saved_errors_in_request
from cornice import Service


crud = Service(name='crud',
               path='/furet-ui/crud',
               description='Generic Crud',
               cors_origins=('*',),
               cors_credentials=True,
               installed_blok=current_blok())


@crud.post()
def crud_create(request):
    registry = request.anyblok.registry
    data = request.json_body
    model = data['model']
    uuid = data['uuid']
    changes = deepcopy(data['changes'])

    with saved_errors_in_request(request):
        obj = registry.FuretUI.CRUD.create(model, uuid, changes)
        # create_or_update(registry, changes, firstmodel=model)
        return {
            'pks': obj.to_primary_keys(),
        }


@crud.get()
def crud_read(request):
    registry = request.anyblok.registry
    return registry.FuretUI.CRUD.read(request)


@crud.patch()
def crud_update(request):
    registry = request.anyblok.registry
    data = request.json_body
    model = data['model']
    pks = data['pks']
    changes = deepcopy(data['changes'])

    with saved_errors_in_request(request):
        obj = registry.FuretUI.CRUD.update(model, pks, changes)
        # create_or_update(registry, changes, firstmodel=model)
        return {
            'pks': obj.to_primary_keys(),
        }


@crud.delete()
def crud_delete(request):
    registry = request.anyblok.registry
    data = request.params
    model = data['model']
    pks = dict(json.loads(data['pks']))

    with saved_errors_in_request(request):
        registry.FuretUI.CRUD.delete(model, pks)
        return {
            'pks': pks,
        }
