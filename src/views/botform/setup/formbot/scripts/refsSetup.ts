import { storeBot } from "@/stores/bot";
import { useCredentialsStore } from "@/stores/credentials";
import { useMessageStore } from "@/stores/message";
import { storeToRefs } from "pinia";
import { computed, reactive, ref } from "vue";

export default function () {
  const progressBar = ref(0);
  const selected = ref(null);
  const queryCourt = ref("");
  const courtOptions = ref<selectCourts[]>([]);
  const overlayFormSubmit = ref(false);
  const { bot, form } = storeToRefs(storeBot());
  const { credentialsSelector } = storeToRefs(useCredentialsStore());
  const { message } = storeToRefs(useMessageStore());
  const selectCredentialsRef = ref<SelectCredentialsRefType>([
    {
      value: null,
      text: "CARREGANDO",
      disabled: true,
    },
  ]);
  const EnabledInputs = reactive<TypeEnabledInputs>({
    xlsx: false,
    creds: false,
    parte_name: false,
    doc_parte: false,
    data_inicio: false,
    data_fim: false,
    polo_parte: false,
    state: false,
    varas: false,
    client: false,
    otherfiles: false,
    confirm_fields: false,
    periodic_task: false,
  });

  const queryCourtOptionsCourt = computed(() => {
    return Array.from(courtOptions.value).filter((item) => {
      if (item.text.toLowerCase().includes(queryCourt.value.toLowerCase())) {
        return true;
      }

      return false;
    });
  });

  const stateOptions = ref([
    { value: null, text: "Selecione um estado", disabled: true },
    { value: "AM", text: "Amazonas" },
  ]);

  return {
    progressBar,
    queryCourtOptionsCourt,
    stateOptions,
    message,
    selected,
    queryCourt,
    courtOptions,
    overlayFormSubmit,
    bot,
    form,
    EnabledInputs,
    credentialsSelector,
    selectCredentialsRef,
  };
}
