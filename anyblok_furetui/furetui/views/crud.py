import json
from copy import deepcopy
from anyblok_pyramid import current_blok
from cornice import Service
from anyblok_furetui.security import authorized_user


crud = Service(name='crud',
               path='/furet-ui/resource/{resource}/crud',
               description='Generic Crud',
               validators=(authorized_user,),
               cors_origins=('*',),
               cors_credentials=True,
               installed_blok=current_blok())


@crud.post()
def crud_create(request):
    registry = request.anyblok.registry
    try:
        data = request.json_body
        model = data['model']
        uuid = data['uuid']
        changes = deepcopy(data['changes'])
        obj = registry.FuretUI.CRUD.create(
            model, uuid, changes, request.authenticated_userid)
        return {
            'pks': obj.to_primary_keys(),
        }
    except registry.FuretUI.UserError as e:
        return {'data': [e.get_furetui_error()]}
    except Exception as e:
        return {'data': [
            registry.FuretUI.UnknownError(str(e)).get_furetui_error()
        ]}


@crud.get()
def crud_read(request):
    registry = request.anyblok.registry
    try:
        return registry.FuretUI.CRUD.read(request)
    except registry.FuretUI.UserError as e:
        return {'data': [e.get_furetui_error()]}
    except Exception as e:
        return {'data': [
            registry.FuretUI.UnknownError(str(e)).get_furetui_error()
        ]}


@crud.patch()
def crud_update(request):
    registry = request.anyblok.registry
    try:
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
    except registry.FuretUI.UserError as e:
        return {'data': [e.get_furetui_error()]}
    except Exception as e:
        return {'data': [
            registry.FuretUI.UnknownError(str(e)).get_furetui_error()
        ]}


@crud.delete()
def crud_delete(request):
    registry = request.anyblok.registry
    try:
        data = request.params
        model = data['model']
        pks = dict(json.loads(data['pks']))

        registry.FuretUI.CRUD.delete(model, pks, request.authenticated_userid)
        return {
            'pks': pks,
        }
    except registry.FuretUI.UserError as e:
        return {'data': [e.get_furetui_error()]}
    except Exception as e:
        return {'data': [
            registry.FuretUI.UnknownError(str(e)).get_furetui_error()
        ]}
