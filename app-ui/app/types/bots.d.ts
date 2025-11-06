type SytemBots = "PROJUDI" | "ESAJ" | "ELAW" | "JUSDS" | "PJE";
type ConfigForm = "file_auth" | "multiple_files" | "only_auth" | "proc_parte" | "only_file" | "pje";
type StatusBot = "Inicializando" | "Em Execução" | "Finalizado";
interface BotInfo {
  Id: number;
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
  status: MessageType;
}

interface Message {
  pid: string;
  message: string;
  message_type: MessageType;
  status: StatusBot;
  start_time: string;
  row: number;
  total: number;
  erros: number;
  sucessos: number;
  restantes: number;
  link: string;
}

interface ValoresContador {
  total: "total";
  sucessos: "sucessos";
  erros: "erros";
  restantes: "restantes";
}
