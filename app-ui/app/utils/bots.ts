import logoEsaj from "~/assets/img/esaj3.png";
import crawjud from "~/assets/img/figure_crawjud.png";
import logoJusBr from "~/assets/img/jusbr.png";
import logoElaw from "~/assets/img/logoelaw.png";
import logoPJE1 from "~/assets/img/pje.png";
import logoProjudi from "~/assets/img/projudilogo.png";

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

  constructor() {}

  async listagemBots() {
    try {
      const response: BotResponse = await api.get("/bots/listagem");

      if (response.data) {
        return response.data.listagem;
      }
    } catch {}

    return [];
  }

  getClassImgLogo(system: system_bots) {
    return this.class_logo[system] || "card-img-top p-4 img-thumbnail imgBot";
  }

  getLogo(system: system_bots) {
    return this.imagesSrc[system] || crawjud;
  }

  handleBotSelected(botInfo: BotInfo) {
    const { $router: router } = useNuxtApp();

    router.push({
      name: `bots-system-type`,
      params: { system: botInfo.system.toLowerCase(), type: botInfo.bot_type.toLowerCase() },
    });
  }
}

export default new Bots();
