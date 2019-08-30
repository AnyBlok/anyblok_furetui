from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.crud_resource import CrudResource, resource
from anyblok_marshmallow import SchemaWrapper
from anyblok_marshmallow.fields import Nested
from marshmallow import fields

MODEL = "Model.User"


class UserRoleSchema(SchemaWrapper):
    model = 'Model.User.Role'


class UserSchema(SchemaWrapper):
    model = MODEL

    class Schema:
        roles = Nested(UserRoleSchema, many=True, only=('name', 'label'))
        password = fields.Str()
        password2 = fields.Str()


@resource(
    collection_path='/api/v1/users',
    path='/api/v1/user/{login}',
    permission='authenticated',
    installed_blok=current_blok()
)
class UsersResource(CrudResource):
    model = MODEL
    default_schema = UserSchema

    def create(self, Model, params=None):
        if params['password'] != params['password2'] or not params['password']:
            self.request.errors.add(
                'body', '400 bad request',
                'Password and confirm password are differents'
            )
            self.request.errors.status = '400'
            return

        values = params.copy()
        del values['password']
        del values['password2']
        del values['roles']
        user = Model.insert(**values)
        self.registry.User.CredentialStore.insert(
            login=params['login'], password=params['password'])
        Role = self.registry.User.Role
        user.roles = Role.query().filter(
            Role.name.in_([x['name'] for x in params['roles']])).all()
        return user

    def update(self, user, params=None):
        values = params.copy()
        if 'roles' in params:
            del values['roles']
            Role = self.registry.User.Role
            user.roles = Role.query().filter(
                Role.name.in_([x['name'] for x in params['roles']])).all()

        password = params.get('password', None)
        password2 = params.get('password2', None)
        if password or password2:
            if password2 != password:
                self.request.errors.add(
                    'body', '400 bad request',
                    'Password and confirm password are differents'
                )
                self.request.errors.status = '400'
                return
            CredentialStore = self.registry.User.CredentialStore
            credential = CredentialStore.query().get(user.login)
            if credential:
                credential.password == password
            else:
                CredentialStore.insert(login=user.login, password=password)

        user.update(**values)
