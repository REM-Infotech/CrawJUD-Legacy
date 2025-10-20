/**
 * @deprecated Este arquivo será descontinuado. Use os novos composables em /composables/
 * - useBotFormState.ts para estado
 * - useBotFormSetup.ts para setup principal
 * - useBotFormComponents.ts para componentes
 * 
 * Para compatibilidade temporária, este setup ainda funciona mas redireciona para os novos composables.
 */

import { api } from "@/controllers/axios";
import { isAxiosError } from "axios";
import { useRouter } from "vue-router";
import { inject } from "vue";
import varas from "../json/varas.json";
import componentsSetup from "./componentsSetup";
import { BOT_FORM_STATE_KEY, BOT_FORM_REFS_KEY, BOT_FORM_OPTIONS_KEY } from "@/composables/useBotFormState";
import type { BotFormState, BotFormRefs, BotFormOptions } from "@/composables/useBotFormState";

type TratamentoArquivosParams = {
  xlsx?: File | File[] | string;
  otherfiles?: File | File[] | string;
};

/**
 * @deprecated Use os novos composables ao invés deste setup
 * Este é mantido apenas para compatibilidade com componentes existentes
 */
export default function () {
  const router = useRouter();
  
  // Injeta o estado dos novos composables se disponível
  const formState = inject<BotFormState>(BOT_FORM_STATE_KEY);
  const formRefs = inject<BotFormRefs>(BOT_FORM_REFS_KEY);
  const formOptions = inject<BotFormOptions>(BOT_FORM_OPTIONS_KEY);
  
  if (!formState || !formRefs || !formOptions) {
    throw new Error(
      'formSetup legado deve ser usado apenas em componentes que recebem o estado via provide/inject. ' +
      'Para componentes principais, use useBotFormState e useBotFormSetup diretamente.'
    );
  }

  const {
    progressBar,
    queryCourtOptionsCourt,
    overlayFormSubmit,
    bot,
    form,
    enabledInputs: EnabledInputs,
    courtOptions,
    queryCourt,
    credentialsSelector,
    message,
    selectCredentialsRef,
    stateOptions,
  } = { ...formState, ...formRefs, ...formOptions };

  const {
    CourtInputView,
    ClasseParteSelectView,
    AnotherFilesInputView,
    PrincipalFileInputView,
    DocumentParteInputView,
    ParteNameInputView,
    ConfirmInputView,
    DataFimView,
    DataInicioView,
    SelectClientView,
    SelectCredentialsView,
    SelectStateView,
    EnableScheduleView,
    ScheduleTaskFormView,
  } = componentsSetup();

  async function handleSubmit(e: Event) {
    if (!bot.value?.id) return;
    e.preventDefault();

    overlayFormSubmit.value = true;

    form.value.bot_id = bot.value.id;
    let msg = "Erro ao Iniciar o robô";
    let _isStarted = false;
    try {
      if (EnabledInputs.xlsx) {
        await TratamentoArquivos({
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

  async function TratamentoArquivos(params: TratamentoArquivosParams) {
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
  
  return {
    progressBar,
    message,
    credentialsSelector,
    selectCredentialsRef,
    handleSubmit,
    EnabledInputs,
    CourtInputView,
    ClasseParteSelectView,
    AnotherFilesInputView,
    PrincipalFileInputView,
    DocumentParteInputView,
    ParteNameInputView,
    ConfirmInputView,
    DataFimView,
    DataInicioView,
    SelectClientView,
    SelectCredentialsView,
    SelectStateView,
    EnableScheduleView,
    ScheduleTaskFormView,
    bot,
    form,
    overlayFormSubmit,
    queryCourt,
    queryCourtOptionsCourt,
    courtOptions,
    varas,
    stateOptions,
  };
}
