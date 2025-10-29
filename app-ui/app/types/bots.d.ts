type SytemBots = "PROJUDI" | "ESAJ" | "ELAW" | "JUSDS" | "PJE";
type ConfigForm = "file_auth" | "multipe_files" | "only_auth" | "proc_parte" | "only_file";

interface BotInfo {
  id: number;
  configuracao_form: ConfigForm;
  display_name: string;
  sistema: SytemBots;
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

interface StartBotPayload {
  pid: string;
  title: string;
  message: string;
  status: "success" | "danger";
}
