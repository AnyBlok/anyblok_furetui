(function () {
    Vue.component('furet-ui-custom-view-login', {
        template: `
            <section class="section">
                <div class="columns is-mobile">
                    <div class="column is-2-desktop is-offset-5-desktop is-4-tablet is-offset-4-tablet is-10-mobile is-offset-1-mobile">
                        <b-select
                            v-model="database"
                            placeholder="Select the database"
                            v-on:change="change"
                            expanded
                        >
                            <option
                                v-for="db in databases"
                                v-bind:value="db"
                                v-bind:key="db"
                            >{{db}}
                            </option>
                        </b-select>
                        <br />
                        <a
                            class="button is-primary"
                            v-on:click="onCallServer"
                            v-bind:style="{width: '100%'}"
                        >
                            {{ $t('views.clients.login.button') }}
                        </a>
                    </div>
                </div>
            </section>`,
        computed: {
            databases () {
                const state = this.$store.state.data.client.Login;
                if (state != undefined) return state.databases || [];
                return [];
            },
            database () {
                const state = this.$store.state.data.client.Login;
                if (state != undefined) return state.database || '';
                return '';
            },
        },
        methods: {
            onCallServer () {
                json_post_dispatch_all('/client/login', {database: this.database});
            },
            change (value) {
                this.$store.commit('UPDATE_CLIENT', {
                    viewName: 'Login',
                    database: value,
                });
            },
        },
    });
})();
