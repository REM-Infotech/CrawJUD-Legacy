<script setup lang="ts">
import { LogsBotSocket } from "@/main";
import { useStoreLogsBot } from "@/stores/bot/logs";
import { storeToRefs } from "pinia";

import { onMounted } from "vue";
import ChartView from "./components/ChartView.vue";
import LogsCardView from "./components/LogsCardView.vue";

const storeLogs = useStoreLogsBot();

const { current_pid, contentRef, link_file } = storeToRefs(storeLogs);

function stopBotExecution() {
  LogsBotSocket.emit("stop_bot", { data: { pid: current_pid.value } });
}

onMounted(() => {
  link_file.value = "#";
});
</script>

<template>
  <div ref="contentRef" class="container-fluid" id="executions">
    <div class="card">
      <div class="card-header">
        <div class="d-flex justify-content-between align-items-center">
          <h4>Estatisticas</h4>
          <div class="d-flex gap-2">
            <a
              :class="link_file !== '#' ? 'btn btn-success' : 'btn btn-outline-success disabled'"
              :aria-disabled="link_file !== '#' ? false : true"
              id="download-button"
              :href="link_file"
            >
              Baixar Documento
            </a>
            <button
              @click="stopBotExecution"
              type="button"
              class="btn btn-warning"
              id="stop_execut"
            >
              Encerrar Execução
            </button>
          </div>
        </div>
      </div>
      <div class="card-body bg-warning bg-opacity-75">
        <div class="row">
          <div class="col-xl-6 col-md-6">
            <LogsCardView />
          </div>
          <div class="col-xl-6 col-md-6">
            <ChartView />
          </div>
        </div>
      </div>
      <div class="card-footer">
        <br />
      </div>
    </div>
  </div>
</template>

<style lang="css" scoped>
.container-fluid {
  padding-right: 300px;
  padding-left: 300px;
  height: 100%;
  max-height: calc(100% - 50px);
}

.card {
  border-radius: 10px;
  height: 100%;
}
</style>
