import { storeBot } from "@/stores/bot";
import { useCredentialsStore } from "@/stores/credentials";
import { useMessageStore } from "@/stores/message";
import { storeToRefs } from "pinia";
import { computed, reactive, ref, provide, inject, type Ref, type Reactive } from "vue";

// Chaves para provide/inject
export const BOT_FORM_STATE_KEY = Symbol('bot-form-state');
export const BOT_FORM_REFS_KEY = Symbol('bot-form-refs');
export const BOT_FORM_OPTIONS_KEY = Symbol('bot-form-options');

/**
 * Interface para o estado das referências do formulário
 */
export interface BotFormRefs {
  progressBar: Ref<number>;
  queryCourt: Ref<string>;
  courtOptions: Ref<selectCourts[]>;
  overlayFormSubmit: Ref<boolean>;
  selectCredentialsRef: Ref<SelectCredentialsRefType>;
}

/**
 * Interface para o estado das opções do formulário
 */
export interface BotFormOptions {
  queryCourtOptionsCourt: Ref<selectCourts[]>;
  stateOptions: Ref<{ value: string | null; text: string; disabled?: boolean }[]>;
}

/**
 * Interface para o estado completo do formulário do bot
 */
export interface BotFormState {
  bot: Ref<BotRecord | null>;
  form: Ref<TypeFormBot>;
  enabledInputs: Reactive<TypeEnabledInputs>;
  credentialsSelector: Ref<CredentialsSelectorRecord>;
  message: Ref<string>;
}

/**
 * Composable para gerenciar o estado do formulário do bot
 * Centraliza todas as referências reativas e estado do formulário
 */
export function useBotFormState(): BotFormState & BotFormRefs & BotFormOptions {
  const botStore = storeBot();
  const credentialsStore = useCredentialsStore();
  const messageStore = useMessageStore();
  
  // Usar storeToRefs para manter reatividade
  const { bot, form } = storeToRefs(botStore);
  const { credentialsSelector } = storeToRefs(credentialsStore);
  const { message } = storeToRefs(messageStore);

  // Referências reativas
  const progressBar = ref(0);
  const queryCourt = ref("");
  const courtOptions = ref<selectCourts[]>([]);
  const overlayFormSubmit = ref(false);
  
  const selectCredentialsRef = ref<SelectCredentialsRefType>([
    {
      value: null,
      text: "CARREGANDO",
      disabled: true,
    },
  ]);

  // Estado dos inputs habilitados
  const enabledInputs = reactive<TypeEnabledInputs>({
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

  // Opções computadas
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
    // Estado principal
    bot,
    form,
    enabledInputs,
    credentialsSelector,
    message,
    
    // Referências
    progressBar,
    queryCourt,
    courtOptions,
    overlayFormSubmit,
    selectCredentialsRef,
    
    // Opções computadas
    queryCourtOptionsCourt,
    stateOptions,
  };
}

/**
 * Provider para disponibilizar o estado do formulário para componentes filhos
 */
export function provideBotFormState() {
  const formState = useBotFormState();
  
  // Separa o estado em diferentes chaves para injeção mais específica
  const state: BotFormState = {
    bot: formState.bot,
    form: formState.form,
    enabledInputs: formState.enabledInputs,
    credentialsSelector: formState.credentialsSelector,
    message: formState.message,
  };
  
  const refs: BotFormRefs = {
    progressBar: formState.progressBar,
    queryCourt: formState.queryCourt,
    courtOptions: formState.courtOptions,
    overlayFormSubmit: formState.overlayFormSubmit,
    selectCredentialsRef: formState.selectCredentialsRef,
  };
  
  const options: BotFormOptions = {
    queryCourtOptionsCourt: formState.queryCourtOptionsCourt,
    stateOptions: formState.stateOptions,
  };
  
  provide(BOT_FORM_STATE_KEY, state);
  provide(BOT_FORM_REFS_KEY, refs);
  provide(BOT_FORM_OPTIONS_KEY, options);
  
  return formState;
}

/**
 * Injeta o estado principal do formulário
 */
export function useBotFormStateInjected(): BotFormState {
  const state = inject<BotFormState>(BOT_FORM_STATE_KEY);
  if (!state) {
    throw new Error('useBotFormStateInjected deve ser usado dentro de um componente que provê BOT_FORM_STATE_KEY');
  }
  return state;
}

/**
 * Injeta as referências do formulário
 */
export function useBotFormRefsInjected(): BotFormRefs {
  const refs = inject<BotFormRefs>(BOT_FORM_REFS_KEY);
  if (!refs) {
    throw new Error('useBotFormRefsInjected deve ser usado dentro de um componente que provê BOT_FORM_REFS_KEY');
  }
  return refs;
}

/**
 * Injeta as opções do formulário
 */
export function useBotFormOptionsInjected(): BotFormOptions {
  const options = inject<BotFormOptions>(BOT_FORM_OPTIONS_KEY);
  if (!options) {
    throw new Error('useBotFormOptionsInjected deve ser usado dentro de um componente que provê BOT_FORM_OPTIONS_KEY');
  }
  return options;
}