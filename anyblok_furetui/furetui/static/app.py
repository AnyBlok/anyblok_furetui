from vue import VueComponent, Vue
from vue.utils import js_lib

VueRouter = js_lib("VueRouter")
Vue.use(VueRouter)
router = VueRouter.new(dict(routes=[
    {'name': 'home', 'path': '/', 'component': {'template': '<homepage />'}},
    {'name': 'cp1', 'path': '/cp1', 'component': {'template': '<cp1 />'}},
    {'name': 'cp2', 'path': '/cp2', 'component': {'template': '<cp2 />'}},
]))

axios = js_lib("axios")


class HomePage(VueComponent):
    counter = 0
    template = """
        <nav class="level">
            <div class="level-item has-text-centered">
                <div>
                    <p class="heading">Tweets</p>
                    <p class="title">3,456</p>
                </div>
            </div>
            <div class="level-item has-text-centered">
                <div>
                    <p class="heading">Following</p>
                    <p class="title">123</p>
                </div>
            </div>
            <div class="level-item has-text-centered">
                <div>
                    <p class="heading">Followers</p>
                    <p class="title">456K</p>
                </div>
            </div>
            <div class="level-item has-text-centered">
                <div>
                    <p class="heading">Likes</p>
                    <p class="title">{{ counter }}</p>
                </div>
            </div>
        </nav>
    """

    def mounted(self):
        res = axios.get('https://api.coindesk.com/v1/bpi/currentprice.json')

        def callback(response):
            self.counter = response.data.bpi.EUR.rate

        res.then(callback)


HomePage.register('homepage')


class Cp1(VueComponent):
    template = """
        <div class="buttons">
            <b-button type="is-primary">Primary</b-button>
            <b-button type="is-success">Success</b-button>
            <b-button type="is-danger">Danger</b-button>
            <b-button type="is-warning">Warning</b-button>
            <b-button type="is-info">Info</b-button>
            <b-button type="is-link">Link</b-button>
            <b-button type="is-light">Light</b-button>
            <b-button type="is-dark">Dark</b-button>
            <b-button type="is-text">Text</b-button>
        </div>
    """


Cp1.register('cp1')


class Cp2(VueComponent):
    template = """
        <b-field label="Select a date">
            <b-datepicker
                placeholder="Click to select..."
                icon="calendar-today"
            >
            </b-datepicker>
        </b-field>
    """


Cp2.register('cp2')


class App(VueComponent):

    @classmethod
    def init_dict(cls):
        init_dict = super(App, cls).init_dict()
        init_dict.update(router=router)
        return init_dict

    template = """
        <div>
            <section class="hero">
                <div class="hero-head">
                    <nav class="navbar">
                        <div class="container">
                            <div class="navbar-brand">
                                <a class="navbar-item">
                                    <img
                                        src="https://bulma.io/images/bulma-type-white.png"
                                        alt="Logo">
                                </a>
                                <span class="navbar-burger burger"
                                      data-target="navbarMenuHeroA"
                                >
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </span>
                            </div>
                            <div id="navbarMenuHeroA" class="navbar-menu">
                                <div class="navbar-end">
                                    <router-link :to="{name: 'cp1'}">
                                        CP 1
                                    </router-link>
                                    <router-link :to="{name: 'cp2'}">
                                        CP 2
                                    </router-link>
                                </div>
                            </div>
                        </div>
                    </nav>
                </div>
            </section>
            <div class="container">
                <router-view></router-view>
            </div>
        </div>
    """


App("#app")
