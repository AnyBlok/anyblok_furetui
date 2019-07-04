from vue import VueComponent
from routes import routes


class FuretUiHomePage(VueComponent):
    template = "#FuretUiHomePage"


FuretUiHomePage.register('homepage')
routes.append({'path': '/', 'component': {'template': '<homepage />'}})
