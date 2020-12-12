defineComponent('furet-ui-appbar-user-dropmenu', {
  prototype: {
    methods: {
      logOut() {
        axios.post('/furetui/logout')
          .then((res) => {
            if (res.data.global !== undefined) this.$store.commit('UPDATE_GLOBAL', res.data.global);
            if (res.data.menus !== undefined) this.$store.commit('UPDATE_MENUS', res.data.menus);
            if (res.data.lang !== undefined) updateLang(res.data.lang);
            if (res.data.langs !== undefined) updateLocales(res.data.langs);
            this.$store.commit('LOGOUT');
            this.$router.push('/');
          });
      },
    },
  },
});
