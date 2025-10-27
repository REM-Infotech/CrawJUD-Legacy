class Authentication {
  constructor() {}

  async authenticate(form: FormData) {
    const { $api, $toast, $router } = useNuxtApp();
    let message: string = "Erro ao realizar login";
    let message_type: string = "error";
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

    $toast.add({
      severity: message_type,
      summary: message_summary,
      detail: message,
      life: 3000,
    });

    if (message_type === "success") {
      $router.push({ name: "terminal" });
    }
  }
}

export default new Authentication();
