type keySystems = "PJE" | "PROJUDI" | "ESAJ";
type keyStates = "AM";
type Varas = { [key: string]: string };
type Classification = "JURIDICO" | "ADMINISTRATIVO" | "INTERNO";
type FormConfig =
  | "only_auth"
  | "file_auth"
  | "multiple_files"
  | "only_file"
  | "pautas"
  | "proc_parte";

interface JsonVaras {
  [key: string | keySystems]: {
    [key: string | keyStates]: Varas;
  };
}
