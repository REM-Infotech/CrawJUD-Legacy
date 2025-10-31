class Authentication {
  constructor() {}

  async login(form: FormData) {
    const { $router } = useNuxtApp();

    try {
      const resp = await api.post("/auth/login", form);

      if (resp.data.message) {
        notify.show({
          title: "Sucesso!",
          message: String(resp.data?.message),
          type: "success",
          duration: 2000,
        });
        $router.push({ name: "dashboard" });
      }
    } catch {
      //
    }
  }

  async logout() {
    const { $router } = useNuxtApp();

    try {
      await api.post("/auth/logout");
    } catch {
      //
    }
    notify.show({
      type: "info",
      title: "Info",
      message: "Sessão encerrada!",
      duration: 2000,
    });
    $router.push({ name: "index" });
  }
}

export default new Authentication();
