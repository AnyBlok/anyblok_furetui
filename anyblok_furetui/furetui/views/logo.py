from anyblok_pyramid import current_blok
from pyramid.httpexceptions import HTTPFound
from cornice import Service


logo = Service(name='logo',
               path='/furet-ui/logo',
               description='Redirect to static logo',
               cors_origins=('*',),
               installed_blok=current_blok())


@logo.get()
def get_global_init(request):
    return HTTPFound('/furetui/static/logo.png')
