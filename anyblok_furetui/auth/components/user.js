defineComponent('users-list', {
    template: '#UsersList',
    prototype: {
        data() {
            return {
                sortField: 'last_name',
                sortOrder: 'asc',
                filters: [
                    {
                        key: 'first_name',
                        mode: 'include',
                        label: this.$i18n.t('users.first_name'),
                        op: 'or-ilike',
                        values: [],
                    },
                    {
                        key: 'last_name',
                        mode: 'include',
                        label: this.$i18n.t('users.last_name'),
                        op: 'or-ilike',
                        values: [],
                    },
                    {
                        key: 'email',
                        mode: 'include',
                        label: this.$i18n.t('users.email'),
                        op: 'or-ilike',
                        values: [],
                    },
                    {
                        key: 'roles.label',
                        mode: 'include',
                        label: this.$i18n.t('users.roles'),
                        op: 'or-ilike',
                        values: [],
                    },
                ],
                filterSearch: '',
            }
        },
        methods: {
            goToPage(row) {
                this.$router.push({name: 'user_page', params: {login: row.login}});
            },
            goToNew() {
                this.$router.push({name: 'user_new'});
            },
        },
    },
});

defineComponent('user-new', {
    template: '#UserNew',
    prototype: {
        data() {
            return {
                user: {
                    roles: [],
                },
            }
        },
        computed: {
            roles () {
                const roles = [];
                this.$store.state.global.roles.forEach((role) => {
                    roles.push({name: role.name, label: role.label});
                });
                return roles;
            },
        },
        methods: {
            goToPage(response) {
                this.$router.push({
                    name: 'user_page', 
                    params: {login: response.login}
                });
            },
            goToList() {
                this.$router.push({name: 'users'});
            },
        },
    },
});

defineComponent('user-page', {
    template: '#UserPage',
    prototype: {
        props: ['login'],
        data() {
            return {
                isCardModalActive: false,
                password: '',
                password2: '',
                errors: [],
                loading: false,
            }
        },
        computed: {
            getRestApiUrl() {
                return '/api/v1/user/' + this.login;
            },
            empty_message() {
                if (this.password != '') return '';
                return this.$i18n.t('users.update_password.empty')
            },
            not_same_message() {
                if (this.password == this.password2) return '';
                return this.$i18n.t('users.update_password.not_same')
            },
        },
        methods: {
            goToPage(response) {
                this.$router.push({
                    name: 'user_page', 
                    params: {login: response.login}
                });
            },
            goToEdit() {
                this.$router.push({name: 'user_edit', params: {login: this.login}});
            },
            goToList() {
                this.$router.push({name: 'users'});
            },
            update_password() {
                this.errors = [];
                this.loading = true;
                axios.patch(this.getRestApiUrl, {password: this.password, password2: this.password2})
                .then((response) => {
                  this.loading = false;
                  this.password = '';
                  this.password2 = '';
                  this.close_modal()
                })
                .catch((error) => {
                  this.errors = error.response.data.errors;
                  this.loading = false;
                });
            },
            open_modal() {
                this.isCardModalActive = true;
            },
            close_modal() {
                this.isCardModalActive = false;
            },
        },
    },
});


defineComponent('user-edit', {
    template: '#UserEdit',
    prototype: {
        props: ['login'],
        computed: {
            roles () {
                const roles = [];
                this.$store.state.global.roles.forEach((role) => {
                    roles.push({name: role.name, label: role.label});
                });
                return roles;
            },
            getRestApiUrl () {
                return '/api/v1/user/' + this.login;
            },
        },
        methods: {
            goToList() {
                this.$router.push({name: 'users'});
            },
            goToPage(response) {
                this.$router.push({name: 'user_page', login: response.login});
            },
            get_body(initial_user, user) {
                const body = {}
                if (user.first_name != initial_user.first_name) body.first_name = user.first_name.trim();
                if (user.last_name != initial_user.last_name) body.last_name = user.last_name.trim();
                if (user.email != initial_user.email) body.email = user.email.trim();
                if ((user.roles.length != initial_user.roles.length) || _.difference(user.roles, initial_user.roles).length) body.roles = user.roles;
                return body;
            },
        },
    },
});

defineResource('users', {path: 'users', templateName: 'users-list', mustBeAuthenticated: true})
defineResource('user_new', {path: 'user/new', templateName: 'user-new', mustBeAuthenticated: true})
defineResource('user_page', {path: 'user/page/:login', templateName: 'user-page', props: ['login'], mustBeAuthenticated: true})
defineResource('user_edit', {path: 'user/edit/:login', templateName: 'user-edit', props: ['login'], mustBeAuthenticated: true})
