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
defineResource('users-list', {path: 'users', mustBeAuthenticated: true})
