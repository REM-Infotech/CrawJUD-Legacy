class Authentication {
  constructor() {}

  async login(form: FormData) {
    const { $api, $toast, $router } = useNuxtApp();

    let message: string = "Erro ao realizar login";
    let message_type: "danger" | "success" = "danger";
    let message_summary: string = "Erro";

    try {
      const resp = await $api.post("/auth/login", form);

      if (resp.data.message) {
        message = resp.data.message;
        message_type = "success";
        message_summary = "Sucesso!";
      }
    } catch {
      //
    }

    $toast.create({
      variant: message_type,
      title: message_summary,
      body: message,
    });

    if (message_type === "success") {
      $router.push({ name: "dashboard" });
    }
  }

  async logout() {
    const { $api, $toast, $router } = useNuxtApp();

    try {
      await $api.post("/auth/logout");
    } catch (err) {
      console.log(err);
      //
    }

    $toast.create({
      variant: "info",
      title: "Info",
      body: "Sessão encerrada!",
    });

    $router.push({ name: "index" });
  }
}

export default new Authentication();
