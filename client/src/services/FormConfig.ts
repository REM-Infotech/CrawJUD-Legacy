import { useModal } from "bootstrap-vue-next";
import { ref } from "vue";
import { $ } from "../main";

export const current_bot = ref();

export default function () {
  // const vars
  const { show } = useModal("ModalMessage");
  const table_file = ref();
  const FilesListable = ref<{ index: number; file: [UploadableFile, string] }[]>([]);
  const files = ref<UploadableFile[]>([]);

  const columns = [
    {
      data: "index",
      title: "#",
    },
    {
      data: "file",
      title: "Nome do arquivo",
    },
  ];

  // variables
  let messages_xlsx: string[] = [];

  // functions
  function addFiles(newFiles) {
    const XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
    const filesArray = [...newFiles];

    // Verifica quantos arquivos XLSX estão sendo adicionados
    const xlsxFiles = filesArray.filter((file) => file.type === XLSX_TYPE);
    if (xlsxFiles.length > 1) {
      messages_xlsx.push(
        "Não foi possível adicionar mais de um arquivo XLSX. Apenas o primeiro será adicionado.",
      );
      // Remove os arquivos XLSX adicionais, mantendo apenas o primeiro
      newFiles = filesArray.filter((file, index, arr) => {
        if (file.type !== XLSX_TYPE) return true;
        return arr.findIndex((f) => f.type === XLSX_TYPE) === index;
      });
    }

    // Use o tamanho atual da lista para indexar os novos itens
    let i = FilesListable.value.length;

    const newUploadableFiles = [...newFiles]
      .map((file) => new UploadableFile(file))
      .filter((file) => {
        if (file.type === XLSX_TYPE) {
          if (xlsxfileExists(file.type)) {
            messages_xlsx.push(
              `Não foi possível adicionar o arquivo <span class='fw-bold'>"${file.name}"</span>, pois já existe uma planilha adicionada!`,
            );
            return false;
          }
        }

        if (!fileExists(file.name)) {
          FilesListable.value.push({
            index: i,
            file: [file, file.file.name],
          });
          i++;
          return true;
        }
        return false;
      });
    files.value = files.value.concat(newUploadableFiles);

    if (messages_xlsx.length > 0) {
      let html_message = "";

      messages_xlsx.forEach((message) => {
        html_message = html_message + `<p>${message}</p>`;
      });
      $("#message").html(html_message);
      show();
      messages_xlsx = [];
    }
  }

  function fileExists(otherName) {
    return files.value.some(({ name }) => name === otherName);
  }

  function xlsxfileExists(TypeFile) {
    return files.value.some(({ type }) => type === TypeFile);
  }

  function removeFile(file) {
    const index = files.value.indexOf(file);

    if (index > -1) files.value.splice(index, 1);
  }

  return {
    files,
    addFiles,
    removeFile,
    FilesListable,
    table_file,
    columns,
  };
}

class UploadableFile {
  file: File;
  name: string;
  id: unknown;
  url: string;
  status: string | null;
  type: string;
  constructor(file) {
    this.file = file;
    this.name = file.name;
    this.id = `${file.name}-${file.size}-${file.lastModified}-${file.type}`;
    this.url = URL.createObjectURL(file);
    this.status = null;
    this.type = file.type;
  }
}
