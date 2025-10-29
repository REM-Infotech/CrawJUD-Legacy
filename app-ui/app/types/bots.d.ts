type system_bots = "PROJUDI" | "ESAJ" | "ELAW" | "JUSDS" | "PJE";

interface BotInfo {
  id: number;
  display_name: string;
  sistema: system_bots;
  descricao: string;
  categoria: string;
}

interface BotPayload {
  listagem: BotInfo[];
}

interface CredenciaisSelect {
  value: number | null | undefined;
  text: string;
}

interface CredenciaisPayload {
  credenciais: CredenciaisSelect[];
}
