import { defineStore } from "pinia";

export default defineStore("botStore", () => {
  const bot = ref<BotInfo>();

  return { bot };
});
