import { storeToRefs } from "pinia";
import logoEsaj from "~/assets/img/esaj3.png";
import crawjud from "~/assets/img/figure_crawjud.png";
import logoJusBr from "~/assets/img/jusbr.png";
import logoElaw from "~/assets/img/logoelaw.png";
import logoPJE1 from "~/assets/img/pje.png";
import logoProjudi from "~/assets/img/projudilogo.png";

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

  constructor() {}

  public loadPlugins() {
    const route = useRoute();
    const { $router: router, $pinia: pinia, $toast: toast } = useNuxtApp();
    const store = storeToRefs(botStore(pinia));
    return { store, router, toast, pinia, route };
  }

  async listagemBots() {
    const response = await api.get<BotPayload>("/bots/listagem", { withCredentials: true });
    return response.data.listagem;
  }

  getClassImgLogo(system: SytemBots) {
    return this.class_logo[system] || "card-img-top p-4 img-thumbnail imgBot";
  }

  getLogo(system: SytemBots) {
    return this.imagesSrc[system] || crawjud;
  }

  handleBotSelected(bot_selected: BotInfo) {
    const { $router: router } = useNuxtApp();
    const { bot } = storeToRefs(botStore());

    bot.value = bot_selected;
    router.push({
      name: `bots-system-type`,
      params: {
        system: bot_selected.sistema.toLowerCase(),
        type: bot_selected.categoria.toLowerCase(),
      },
    });
  }
}

export default new Bots();
