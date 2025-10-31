type FormComponentRecord = Record<ConfigForm, Component | undefined>;
type RecordFileAuthForm = { ArquivoXlsx: File | undefined; Credential: string | null };
type RecordOnlyFileForm = { ArquivoXlsx: File | undefined };
type RecordOnlyAuthForm = { Credential: string | null };
type RecordMultipleFilesForm = {
  ArquivoXlsx: File | undefined;
  OutrosArquivos: File[] | undefined;
  Credential: string | null;
};

interface formManager {
  FormBot: FormData;
  bot: Ref<BotInfo>;
  fileSocket: Socket;
  LoadCredential(selectedCredential: string | undefined): void;
  uploadXlsx(xlsxFile: File | undefined): Promise<void>;
  uploadMultipleFiles(xlsxFile: File[] | undefined): Promise<void>;
}
