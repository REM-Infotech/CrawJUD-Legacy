import { storeToRefs } from "pinia";
import FileAuth from "./_forms/FileAuth.vue";
import MultipleFiles from "./_forms/MultipleFiles.vue";
import FileUploader from "./interfaces/FileUploader";

const FormComponents: FormComponentRecord = {
  file_auth: FileAuth,
  multipe_files: MultipleFiles,
  only_auth: undefined,
  proc_parte: undefined,
  only_file: undefined,
};

class FormManager extends FileUploader {
  constructor() {
    super();
  }

  public async HandleSubmit(ev: Event) {
    ev.preventDefault();

    const { bot } = storeToRefs(botStore());

    this.FormBot.append("bot_id", bot.value?.Id as unknown as string);

    const endpoint = `/bot/${bot.value?.sistema.toLowerCase()}/run`;
    const resp = await api.post<StartBotPayload>(endpoint, this.FormBot);
    const data = resp.data;

    notify.show({
      title: data.title,
      message: data.message,
      type: data.status,
      duration: 5000,
    });
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

  public LoadCredential(credentialId: string | null): void {
    if (credentialId) {
      this.FormBot.append("credencial_id", credentialId);
    }
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
