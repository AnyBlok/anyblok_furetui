defineComponent('login', {
  template: '#Login',
  prototype: {
    methods: {
      getBody() {
          return {};
      },
      logIn() {
        axios.post('/furetui/login', this.getBody())
          .then((res) => {
            if (res.data.global !== undefined) this.$store.commit('UPDATE_GLOBAL', res.data.global);
            if (res.data.menus !== undefined) this.$store.commit('UPDATE_MENUS', res.data.menus);
            if (res.data.lang !== undefined) updateLang(res.data.lang);
            if (res.data.langs !== undefined) updateLocales(res.data.langs);
            const userName = this.$store.state.global.userName;
            this.$notify({
              title: `Welcome ${userName}`,
              text: 'Your are logged',
              duration: 5000,
            });
            this.$store.commit('LOGIN')
            if (this.$route.query.redirect !== undefined) this.$router.push(this.$route.query.redirect);
            else this.$router.push('/');
          })
      },
    },
  },
});
