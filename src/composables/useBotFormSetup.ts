import { api } from "@/controllers/axios";
import { isAxiosError } from "axios";
import { useRouter } from "vue-router";
import { onBeforeMount, onMounted, onUnmounted } from "vue";
import varas from "@/views/botform/setup/formbot/json/varas.json";
import formConfig from "@/views/botform/setup/formbot/json/formconfig.json";
import type { BotFormState, BotFormRefs, BotFormOptions } from "./useBotFormState";

/**
 * Parâmetros para tratamento de arquivos
 */
type TratamentoArquivosParams = {
  xlsx?: File | File[] | string;
  otherfiles?: File | File[] | string;
};

/**
 * Composable para setup principal do formulário do bot
 * Centraliza a lógica de inicialização, lifecycle hooks e submissão do formulário
 * 
 * @param formState - Estado do formulário injetado
 * @param formRefs - Referências do formulário injetadas
 * @param formOptions - Opções do formulário injetadas
 * @returns Funções e dados necessários para o componente principal
 */
export function useBotFormSetup(
  formState: BotFormState,
  formRefs: BotFormRefs,
  _formOptions: BotFormOptions
) {
  const router = useRouter();
  
  const {
    bot,
    form,
    enabledInputs,
    message,
  } = formState;
  
  const {
    overlayFormSubmit,
    courtOptions,
  } = formRefs;

  /**
   * Configura os inputs habilitados baseado na configuração do bot
   */
  function setupEnabledInputs() {
    if (!bot.value?.classification || !bot.value.form_cfg) return;

    const classification = bot.value.classification as Classification;
    const formcfg = bot.value.form_cfg as FormConfig;
    const formconfigClass = formConfig[classification] as FormConfigRecord;
    const formconfigList = formconfigClass[formcfg];

    Object.entries(enabledInputs).map(([key, value]) => {
      const isKey = Array.from(formconfigList).find((val) => val === key);

      if (isKey) {
        enabledInputs[key] = !value;
      }
    });
  }

  /**
   * Configura as opções de tribunais baseado no sistema e estado do bot
   */
  function setupCourtOptions() {
    if (!(bot.value?.system || bot.value?.state)) return;
    if (bot.value.state.toLowerCase() !== "EVERYONE".toLowerCase()) {
      const varasRecord = varas as unknown as JsonVaras;
      const courts: selectCourts[] = [];

      const system = bot.value?.system.toUpperCase() as unknown as keySystems;
      const state = bot.value?.state.toUpperCase() as unknown as keyStates;

      const courtsJson = varasRecord[system][state];

      Object.entries(courtsJson).map(([key, value], index) => {
        courts.push({ value: key, text: value, id: index });
      });
      courtOptions.value.push(...courts);
    }
  }

  /**
   * Trata os arquivos antes do envio
   * 
   * @param params - Parâmetros contendo os arquivos xlsx e outros arquivos
   */
  async function tratamentoArquivos(params: TratamentoArquivosParams) {
    const { xlsx, otherfiles } = params;

    const fileListXlsx = Array.isArray(xlsx) ? (xlsx as File[]) : [xlsx as File];
    for (const f of fileListXlsx) {
      const file = f as File;
      form.value.xlsx = file.name;
    }
    
    if (otherfiles) {
      const newFileList = [];
      const otherFilesList = Array.isArray(otherfiles) ? otherfiles : [otherfiles];
      for (const f of otherFilesList) {
        const file = f as File;
        newFileList.push(file.name);
      }
      form.value.otherfiles = newFileList;
    }
  }

  /**
   * Manipula a submissão do formulário
   * 
   * @param e - Evento de submissão do formulário
   */
  async function handleSubmit(e: Event) {
    if (!bot.value?.id) return;
    e.preventDefault();

    overlayFormSubmit.value = true;

    form.value.bot_id = bot.value.id;
    let msg = "Erro ao Iniciar o robô";
    let _isStarted = false;
    
    try {
      if (enabledInputs.xlsx) {
        await tratamentoArquivos({
          xlsx: form.value.xlsx as File,
          otherfiles: form.value.otherfiles as File[],
        });
      }

      const Form = new FormData();

      Object.entries(form.value).map(([key, value]) => {
        if (value) {
          if (key !== "otherfiles") {
            Form.append(key, String(value));
          } else if (key === "otherfiles") {
            const other_files: string[] = [];
            console.log(value);
            if (Array.isArray(value)) {
              value.forEach((file) => {
                other_files.push(String(file));
              });
            }

            Form.append("otherfiles", other_files.toString());
          }
        }
      });

      const response: BotStartResponse = await api.post("/bot/start_bot", Form, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.data.message && response.data.pid) {
        _isStarted = true;
        msg = response.data.message;
        const pid = response.data.pid;
        router.push({ name: "logs_execution", params: { pid: pid } });
      }
    } catch (err) {
      if (isAxiosError(err) && err.status) {
        if (err.status != 500) {
          router.push({ name: "bots" });
        }
      }
    }

    overlayFormSubmit.value = false;
    message.value = msg;
  }

  /**
   * Limpa o estado dos inputs habilitados
   */
  function clearEnabledInputs() {
    Object.entries(enabledInputs).forEach(([key]) => {
      enabledInputs[key] = false;
    });
  }

  // Lifecycle hooks
  onMounted(() => {
    if (bot.value === null) {
      router.push({ name: "bots" });
    }
  });

  onBeforeMount(() => {
    setupEnabledInputs();
  });

  onBeforeMount(() => {
    setupCourtOptions();
  });

  onUnmounted(() => {
    clearEnabledInputs();
    bot.value = null;
  });

  return {
    handleSubmit,
    varas,
  };
}