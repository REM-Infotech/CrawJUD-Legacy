type FormComponentRecord = Record<ConfigForm, Component | undefined>;
type RecordFileAuthForm = { PlanilhaXlsx: File | undefined; Credencial: string | null };
type RecordOnlyFileForm = { PlanilhaXlsx: File | undefined };
type RecordOnlyAuthForm = { Credencial: string | null };
type RecordMultipleFilesForm = {
  PlanilhaXlsx: File | undefined;
  Anexos: File[] | undefined;
  Credencial: string | null;
};

type FormBot =
  | RecordFileAuthForm
  | RecordMultipleFilesForm
  | RecordOnlyAuthForm
  | RecordOnlyFileForm;

interface formManager {
  FormBot: FormData;
  bot: Ref<BotInfo>;
  fileSocket: Socket;
  LoadCredential(selectedCredential: string | undefined): void;
  uploadXlsx(xlsxFile: File | undefined): Promise<void>;
  uploadMultipleFiles(xlsxFile: File[] | undefined): Promise<void>;
}
