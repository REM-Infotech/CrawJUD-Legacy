import { defineStore } from "pinia";
import { ref } from "vue";

export const useStoreLogsBot = defineStore("logs", () => {
  const listLogs = ref<ArrayBotLogs>([]);
  const totalLogs = ref<number>(0);
  const remainingLogs = ref<number>(0);
  const currentPos = ref<number>(0);
  const totalSuccess = ref<number>(0);
  const totalErrors = ref<number>(0);
  const status = ref<string>("Iniciado");
  const current_pid = ref("");
  const contentRef = ref<HTMLDivElement | null>(null);
  const link_file = ref<string>("#");

  function $reset() {
    listLogs.value = [];
    totalLogs.value = 0;
    remainingLogs.value = 0;
    currentPos.value = 0;
    totalSuccess.value = 0;
    totalErrors.value = 0;
    status.value = "CARREGANDO";
    current_pid.value = "";
    contentRef.value = null;
  }

  return {
    $reset,
    listLogs,
    totalLogs,
    remainingLogs,
    currentPos,
    totalSuccess,
    totalErrors,
    status,
    current_pid,
    contentRef,
    link_file,
  };
});
