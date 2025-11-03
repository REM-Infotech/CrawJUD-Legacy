import { storeToRefs } from "pinia";
import FileAuth from "./_forms/FileAuth.vue";
import MultipleFiles from "./_forms/MultipleFiles.vue";
import OnlyAuth from "./_forms/OnlyAuth.vue";
import OnlyFile from "./_forms/OnlyFile.vue";
import FileUploader from "./interfaces/FileUploader";

const FormComponents: FormComponentRecord = {
  file_auth: FileAuth,
  multiple_files: MultipleFiles,
  only_auth: OnlyAuth,
  proc_parte: undefined,
  only_file: OnlyFile,
  pje: OnlyFile,
};

class FormManager extends FileUploader {
  constructor() {
    super();
  }

  public async HandleSubmit(ev: Event, form: FormBot) {
    ev.preventDefault();
    console.log(form);
    const { bot } = storeToRefs(botStore());

    try {
      const FormBot = Object.fromEntries(
        Object.entries(form)
          .map(([key, value]) => {
            const isArrayFiles = Array.isArray(value) && value.every((v) => v instanceof File);
            const k = Utils.camelToSnake(key);
            if (!value) throw Error(`Campo ${Utils.camelToWords(key)} não informado!`);
            if (value instanceof File) return [k, Utils.formatString(value.name)];
            else if (isArrayFiles) return [k, value.map((file) => Utils.formatString(file.name))];
            return [k, value];
          })
          .filter((entry): entry is [string, any] => Array.isArray(entry) && entry.length === 2),
      );

      FormBot["bot_id"] = bot.value?.Id;
      FormBot["configuracao_form"] = bot.value?.configuracao_form;
      FormBot["sid_filesocket"] = this.fileSocket.id;

      const endpoint = `/bot/${bot.value?.sistema.toLowerCase()}/run`;
      const resp = await api.post<StartBotPayload>(endpoint, FormBot, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      const data = resp.data;

      this.FormBot.delete("bot_id");
      this.FormBot.delete("configuracao_form");

      notify.show({
        title: data.title,
        message: data.message,
        type: data.status,
        duration: 5000,
      });
    } catch (err) {
      if (err instanceof Error) {
        notify.show({
          title: "Erro",
          message: err.message,
          type: "error",
          duration: 5000,
        });
      }
    }
  }

  public getForm() {
    const { $router: router } = useNuxtApp();
    const { bot } = storeToRefs(botStore());

    if (!bot.value || !bot.value.configuracao_form) {
      router.push({ name: "bots" });
      return;
    }

    this.FormBot = new FormData();
    const comp = FormComponents[bot.value.configuracao_form];
    return comp;
  }

  public async RetrieveCredentials() {
    const { bot, optCredenciais } = storeToRefs(botStore());
    if (!bot.value) return;
    optCredenciais.value = [{ value: null, text: "Selecione" }];

    const resp = await api.get<CredenciaisPayload>(
      `/bot/${bot.value?.sistema.toLowerCase()}/credenciais`,
    );
    if (resp.data) {
      optCredenciais.value.push(...resp.data.credenciais);
    }
  }
}

export default new FormManager();
