<script setup lang="ts">
import { LogsBotSocket } from "@/res";
import { useStoreLogsBot } from "@/stores/bot/logs";
import { storeToRefs } from "pinia";
import { nextTick, onBeforeMount, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import MaterialSymbolsPieChartOutline from "~icons/material-symbols/pie-chart-outline?width=24px&height=24px";
import setupLogsExec from "./setupLogsExec";
const { CardContent, SizeCard, MinSizeCard } = setupLogsExec();

const logsStore = useStoreLogsBot();
const {
  listLogs,
  totalLogs,
  status,
  current_pid,
  totalSuccess,
  totalErrors,
  remainingLogs,
  link_file,
} = storeToRefs(logsStore);

const route = useRoute();
const router = useRouter();

const idLI = ref<string>();

function get_logs(logsData: LogsBotRecord, loadCache: boolean = false) {
  setTimeout(() => {
    if (!loadCache) {
      listLogs.value.push(logsData);
    } else if (loadCache) {
      listLogs.value = logsData.messages as unknown as LogsBotRecord[];
    }
    idLI.value = String(logsData.messages.length - 1);
    totalSuccess.value = logsData.success;
    totalErrors.value = logsData.error;
    totalLogs.value = logsData.total;
    remainingLogs.value = logsData.remaining;
    status.value = logsData.status;

    listLogs.value.forEach((item) => {
      if (item.message.includes("http")) {
        link_file.value = String(item.message.split(": ")[1].replace("]", ""));
      }
    });

    remainingLogs.value = logsData.remaining - (logsData.success + logsData.error);
  }, 1500);
}

LogsBotSocket.on("log_execution", get_logs);

onBeforeMount(() => {
  if (!route.params.pid) {
    router.push({ name: "bots" });
  }
  current_pid.value = route.params.pid as string;
  LogsBotSocket.connect();
  LogsBotSocket.emit("join_room", { data: { room: current_pid.value } });
  LogsBotSocket.emit("load_cache", { data: { pid: route.params.pid } }, get_logs);
});

onUnmounted(() => {
  LogsBotSocket.off("load_cache", get_logs);
  LogsBotSocket.off("log_execution", get_logs);
  LogsBotSocket.disconnect();

  logsStore.$reset();
});

const itemLog = ref();

/**
 * Observa mudanças em idLI e faz scroll suave para o elemento correspondente após a transição.
 *
 * @param {Ref<string | undefined>} idLI - Ref que armazena o id do último log.
 * @returns {void} Não retorna valor.
 */
watch(idLI, (newvalue) => {
  // Aguarda o próximo tick para garantir que o elemento foi renderizado pelo TransitionGroup
  if (newvalue !== undefined) {
    nextTick(() => {
      const el = document.querySelector(`li[id="${String(newvalue)}"]`);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "end" });
      }
    });
  }
});
</script>
<template>
  <div class="card fixed-height-card border-0">
    <div class="card-header">
      <div class="row justify-content-between align-items-center">
        <div class="col-md-5">
          <span class="fw-semibold">
            <MaterialSymbolsPieChartOutline class="me-2" />
          </span>
          <span class="fw-semibold">
            Logs Execução {{ current_pid.split("-")[0].toUpperCase() }}
          </span>
        </div>
      </div>
    </div>
    <div class="card-body bg-black overflow-auto" style="min-height: 400px">
      <CardContent
        :SizeCard="SizeCard"
        :MinSizeCard="MinSizeCard"
        class="overflow-y-auto align-items-start justify-content-start"
      >
        <TransitionGroup tag="ul" name="fade" ref="itemLog">
          <li
            v-for="(item, index) in listLogs"
            :key="index"
            :id="String(index)"
            :class="item.type.toLowerCase()"
          >
            <span v-if="item.message.includes('http')">
              <a :href="item.message.split(': ')[1].replace(']', '')">
                {{ item.message.split(": ")[0] }}]
              </a>
            </span>
            <span v-else>
              {{ item.message }}
            </span>
          </li>
        </TransitionGroup>
      </CardContent>
    </div>
    <div class="card-footer small text-muted fw-semibold">
      <span id="status">Status: {{ status }} | Total: {{ totalLogs }}</span>
    </div>
  </div>
</template>

<style lang="css" scoped>
.error {
  color: #bd0707;
  font-weight: bold;
}

.info {
  color: #f1b00bbb;
  font-weight: bold;
}

.warning {
  color: #af3f07;
  font-weight: bold;
}

.success {
  color: #11ab5b;
  font-weight: bold;
}

.log {
  color: #ffffffa8;
  font-weight: bold;
}

.card {
  height: 100%;
  max-height: calc(100% - 25px);
}
</style>
