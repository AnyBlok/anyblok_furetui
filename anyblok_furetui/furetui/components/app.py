from vue import Vue, VueComponent, computed


class FuretUiApp(VueComponent):
    template = "#FuretUiApp"


class FuretUiAppBar(VueComponent):
    template = "#FuretUiAppBar"


class FuretUiAppBarHeader(VueComponent):
    template = "#FuretUiAppBarHeader"

    # data
    isOpen = False


class FuretUiAppBarHeaderBrand(VueComponent):
    template = "#FuretUiAppBarHeaderBrand"


class FuretUiAppBarBody(VueComponent):
    template = "#FuretUiAppBarBody"


class FuretUiAppBarFooter(VueComponent):
    template = "#FuretUiAppBarFooter"

    @computed
    def hasSpaceMenus(self):
        return len(self.store.menus.spaceMenus) != 0


class RouterLink(VueComponent):
    label: str
    to: str

    def goTo(self):
        self.router.push(self.to)


class FuretUiAppBarHeadRouterLink(RouterLink):
    template = "#FuretUiAppBarHeadRouterLink"


class FuretUiAppBarHeadRouterLinkButton(RouterLink):
    icon: str

    template = "#FuretUiAppBarHeadRouterLinkButton"


class FuretUiAppBarUserMenu(VueComponent):
    template = """
        <div class="navbar-end">
            <span v-html="menu" v-for="menu in menus" />
        </div>
    """

    @computed
    def menus(self):
        return self.store.menus.user


class FuretUiAppBarSpacesMenu(VueComponent):
    template = """
        <div class="navbar-start">
            <span v-html="menu" v-for="menu in menus" />
        </div>
    """

    @computed
    def menus(self):
        return self.store.menus.spaces


class FuretUiAppBarSpaceMenus(VueComponent):
    template = """
        <nav class="tabs is-boxed">
            <div class="container">
                <ul>
                    <li v-for="menu in menus">
                        <span v-html="menu" />
                    </li>
                </ul>
            </div>
        </nav>
    """

    @computed
    def menus(self):
        return self.store.menus.spaceMenus


class FuretUiAppBarFootRouterLink(RouterLink):
    template = "#FuretUiAppBarFootRouterLink"


class FuretUiAppBarFootRouterLinkButton(RouterLink):
    icon: str

    template = "#FuretUiAppBarFootRouterLinkButton"


class FuretUiFooter(VueComponent):
    template = "#FuretUiFooter"


FuretUiApp.register('app')
FuretUiAppBar.register('furet-ui-appbar')
FuretUiAppBarHeader.register('furet-ui-appbar-header')
FuretUiAppBarHeaderBrand.register('furet-ui-appbar-header-brand')
FuretUiAppBarBody.register('furet-ui-appbar-body')
FuretUiAppBarFooter.register('furet-ui-appbar-footer')
FuretUiAppBarHeadRouterLink.register('furet-ui-appbar-head-router-link')
FuretUiAppBarHeadRouterLinkButton.register(
    'furet-ui-appbar-head-router-link-button')
FuretUiAppBarFootRouterLink.register('furet-ui-appbar-foot-router-link')
FuretUiAppBarFootRouterLinkButton.register(
    'furet-ui-appbar-foot-router-link-button')
FuretUiFooter.register('furet-ui-footer')
FuretUiAppBarUserMenu.register('furet-ui-appbar-user-menu')
FuretUiAppBarSpacesMenu.register('furet-ui-appbar-spaces-menu')
FuretUiAppBarSpaceMenus.register('furet-ui-appbar-space-menus')
