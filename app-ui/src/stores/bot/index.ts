import { defineStore } from "pinia";
import { reactive, ref } from "vue";
import botListJson from "./botsList.json";

const storeBot = defineStore("bot", () => {
  const jsonlistBot = botListJson as unknown as BotRecord[];
  const botList = ref<BotRecord[]>(jsonlistBot);
  const bot = ref<BotRecord | null>(null);
  const form = reactive<TypeFormBot>({
    bot_id: null,
    xlsx: null,
    creds: null,
    parte_name: null,
    doc_parte: null,
    data_inicio: null,
    data_fim: null,
    polo_parte: null,
    state: null,
    varas: null,
    client: null,
    otherfiles: null,
    confirm_fields: null,
    periodic_task: null,
    task_name: null,
    task_hour_minute: null,
    email_notify: null,
    days_task: null,
    token: null,
  });

  return { bot, botList, form };
});

export { storeBot };
