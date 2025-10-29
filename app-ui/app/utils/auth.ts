class Authentication {
  constructor() {}

  async login(form: FormData) {
    const { $toast, $router } = useNuxtApp();

    let message: string = "Erro ao realizar login";
    let message_type: "danger" | "success" = "danger";
    let message_summary: string = "Erro";

    try {
      const resp = await api.post("/auth/login", form);

      if (resp.data.message) {
        message = resp.data.message;
        message_type = "success";
        message_summary = "Sucesso!";
        $router.push({ name: "dashboard" });
      }
    } catch {
      //
    }

    $toast.create({
      variant: message_type,
      title: message_summary,
      body: message,
      noCloseButton: true,
      noAnimation: true,
      noProgress: true,
      modelValue: 1500,
    });
  }

  async logout() {
    const { $toast, $router } = useNuxtApp();

    try {
      await api.post("/auth/logout");
    } catch {
      //
    }
    $toast.create({
      variant: "info",
      title: "Info",
      body: "Sessão encerrada!",
      noCloseButton: true,
      noAnimation: true,
      noProgress: true,
      modelValue: 1500,
    });
    $router.push({ name: "index" });
  }
}

export default new Authentication();
