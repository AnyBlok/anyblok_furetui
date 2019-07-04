from vue import VueComponent, Vue, VueStore
from vue.utils import js_lib
from routes import routes


VueRouter = js_lib("VueRouter")
Vue.use(VueRouter)


router = VueRouter.new(dict(routes=routes))


class Store(VueStore):
    menus = {
        'spaceMenus': [],
        'spaces': [],
        'user': [],
    }


class App(VueComponent):

    @classmethod
    def init_dict(cls):
        init_dict = super(App, cls).init_dict()
        init_dict.update(router=router, store=Store())
        return init_dict

    template = "<app />"


App("#app")
