import logoEsaj from "~/assets/img/esaj3.png";
import crawjud from "~/assets/img/figure_crawjud.png";
import logoJusBr from "~/assets/img/jusbr.png";
import logoElaw from "~/assets/img/logoelaw.png";
import logoPJE1 from "~/assets/img/pje.png";
import logoProjudi from "~/assets/img/projudilogo.png";
import capa from "./_forms/capa.vue";
import protocolo from "./_forms/protocolo.vue";

class Bots {
  private class_logo: Record<system_bots, string> = {
    PJE: "card-img-top p-4 img-thumbnail imgBot",
    ESAJ: "card-img-top p-4 img-thumbnail imgBot",
    PROJUDI: "card-img-top p-4 img-thumbnail imgBot bg-white",
    ELAW: "card-img-top p-4 img-thumbnail imgBot bg-white",
    JUSDS: "card-img-top p-4 img-thumbnail imgBot bg-white",
  };
  private imagesSrc: Record<system_bots, string> = {
    PROJUDI: logoProjudi,
    ESAJ: logoEsaj,
    ELAW: logoElaw,
    PJE: logoPJE1,
    JUSDS: logoJusBr,
  };

  private forms = {
    capa: capa,
    protocolo: protocolo,
  };

  constructor() {}

  async listagemBots() {
    try {
      const response = await api.get<BotPayload>("/bots/listagem", { withCredentials: true });

      if (response.data) {
        return response.data.listagem;
      }
    } catch {}

    return [] as BotInfo[];
  }

  getClassImgLogo(system: system_bots) {
    return (
      this.class_logo[system.toUpperCase() as system_bots] ||
      "card-img-top p-4 img-thumbnail imgBot"
    );
  }

  getLogo(system: system_bots) {
    return this.imagesSrc[system.toUpperCase() as system_bots] || crawjud;
  }

  handleBotSelected(bot_selected: BotInfo) {
    const { $router: router, $pinia } = useNuxtApp();

    const { bot } = storeToRefs(botStore($pinia));
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
    const { $router: router } = useNuxtApp();
    const route = useRoute();
    const comp = this.forms[route.params.type as "capa"];
    if (!comp) router.push({ name: "bots" });
    return comp;
  }

  async startBot(form: FormData) {
    const { $toast } = useNuxtApp();

    $toast.create({
      title: "Robô inicializado!",
      body: "Código de execução: A1B2C3",
      variant: "success",
      modelValue: 3500,
    });
  }
}

export default new Bots();
