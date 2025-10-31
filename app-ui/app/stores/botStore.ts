import { defineStore } from "pinia";

export default defineStore("botStore", () => {
  const bot = ref<BotInfo>(undefined as unknown as BotInfo);
  const botForm = ref<FormBot>();

  const btnConfirm = ref(false);
  const confirmedState = computed(() => btnConfirm.value);

  const optCredenciais = ref<CredenciaisSelect[]>([{ value: null, text: "Selecione" }]);
  const opcoesCredenciais = computed<CredenciaisSelect[]>(() => optCredenciais.value);

  const currentPos = ref(0);
  const progressBarValue = ref(0);

  const progressBar = computed(() => progressBarValue.value);

  function $reset() {
    bot.value = undefined as unknown as BotInfo;
    botForm.value = undefined;
    optCredenciais.value = [{ value: null, text: "Selecione" }];
  }

  return {
    bot,
    botForm,
    opcoesCredenciais,
    $reset,
    btnConfirm,
    confirmedState,
    optCredenciais,
    progressBar,
    progressBarValue,
    currentPos,
  };
});
