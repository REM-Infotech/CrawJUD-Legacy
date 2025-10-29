import type { Component } from "vue";
import logoEsaj from "~/assets/img/esaj3.png";
import crawjud from "~/assets/img/figure_crawjud.png";
import logoJusBr from "~/assets/img/jusbr.png";
import logoElaw from "~/assets/img/logoelaw.png";
import logoPJE1 from "~/assets/img/pje.png";
import logoProjudi from "~/assets/img/projudilogo.png";
import FileAuth from "./_forms/FileAuth.vue";
import MultipleFiles from "./_forms/MultipleFiles.vue";

class Bots {
  private class_logo: Record<SytemBots, string> = {
    PJE: "card-img-top p-4 img-thumbnail imgBot",
    ESAJ: "card-img-top p-4 img-thumbnail imgBot",
    PROJUDI: "card-img-top p-4 img-thumbnail imgBot bg-white",
    ELAW: "card-img-top p-4 img-thumbnail imgBot bg-white",
    JUSDS: "card-img-top p-4 img-thumbnail imgBot bg-white",
  };
  private imagesSrc: Record<SytemBots, string> = {
    PROJUDI: logoProjudi,
    ESAJ: logoEsaj,
    ELAW: logoElaw,
    PJE: logoPJE1,
    JUSDS: logoJusBr,
  };

  private forms: Record<ConfigForm, Component | undefined> = {
    file_auth: FileAuth,
    multipe_files: MultipleFiles,
    only_auth: undefined,
    proc_parte: undefined,
    only_file: undefined,
  };

  constructor() {}

  public loadPlugins() {
    const route = useRoute();
    const { $router: router, $pinia: pinia, $toast: toast } = useNuxtApp();
    const store = storeToRefs(botStore(pinia));
    return { store, router, toast, pinia, route };
  }

  async listagemBots() {
    try {
      const response = await api.get<BotPayload>("/bots/listagem", { withCredentials: true });
      if (response.data) {
        return response.data.listagem;
      }
    } catch {}

    return [] as BotInfo[];
  }

  getClassImgLogo(system: SytemBots) {
    return this.class_logo[system] || "card-img-top p-4 img-thumbnail imgBot";
  }

  getLogo(system: SytemBots) {
    return this.imagesSrc[system] || crawjud;
  }

  handleBotSelected(bot_selected: BotInfo) {
    const {
      router,
      store: { bot },
    } = this.loadPlugins();

    bot.value = bot_selected;
    router.push({
      name: `bots-system-type`,
      params: {
        system: bot_selected.sistema.toLowerCase(),
        type: bot_selected.categoria.toLowerCase(),
      },
    });
  }

  getComponent() {
    const {
      router,
      store: { bot },
    } = this.loadPlugins();
    if (!bot.value || !bot.value.configuracao_form) {
      router.push({ name: "bots" });
      return;
    }
    const comp = this.forms[bot.value.configuracao_form];
    return comp;
  }

  async startBot(form: FormData) {
    const {
      store: { bot },
      toast,
    } = this.loadPlugins();

    const endpoint = `/bot/${bot.value?.sistema.toLowerCase()}/run/${bot.value?.id}`;
    const resp = await api.post<StartBotPayload>(endpoint, form);
    const data = resp.data;
    toast.create({
      title: data.title,
      body: data.message,
      variant: data.status,
      modelValue: 5000,
    });
  }

  async loadCredentials() {
    const {
      store: { bot, optCredenciais },
    } = this.loadPlugins();
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

export default new Bots();
