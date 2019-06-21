defineComponent('homepage', {
    template: '#FuretUiHomePage',
    prototype: {
        computed: {
            logo() {
                return this.format_url('/furetui/static/logo.png');
            },
            anyblok_logo() {
                return this.format_url('/furetui/static/anyblok.png');
            },
        },
    }
});
