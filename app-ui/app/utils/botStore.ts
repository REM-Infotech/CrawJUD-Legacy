import { defineStore } from "pinia";

export default defineStore("botStore", () => {
  const bot = ref<BotInfo>();
  const botForm = ref<FormData>();
  const opcoesCredenciais = ref<CredenciaisSelect[]>([{ value: null, text: "Selecione" }]);

  function $reset() {
    bot.value = undefined;
    botForm.value = undefined;
    opcoesCredenciais.value = [{ value: null, text: "Selecione" }];
  }

  return { bot, botForm, opcoesCredenciais, $reset };
});
