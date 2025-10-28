type system_bots = "PROJUDI" | "ESAJ" | "ELAW" | "JUSDS" | "PJE";

interface BotInfo {
  id: number;
  display_name: string;
  system: system_bots;
  descricao: string;
  bot_type: string;
}

interface BotResponse extends AxiosResponse {
  data?: {
    listagem: BotInfo[];
  };
}
