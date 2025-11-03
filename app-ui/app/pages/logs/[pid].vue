<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import { Doughnut } from "vue-chartjs";
const chartData = ref([40, 20, 12]);

const LogsSocket = socketio.socket("/bot_logs");

const itemLog = ref<HTMLElement | null>(null); // Ref para o ul
let pid: string;
onMounted(() => {
  const route = useRoute();
  const pid_param: string = route.params.pid as string;

  if (pid_param) {
    pid = pid_param;
    sessionStorage.setItem("pid", pid);
  } else if (!pid_param) {
    pid = sessionStorage.getItem("pid") as string;
  }

  LogsSocket.connect();
  LogsSocket.emit("join_room", { room: pid });
});

LogsSocket.on("logbot", async (data) => {
  receivedLogs.value.push(data);
  Contagem.value = [data.total, data.success_count, data.error_count];
  await nextTick();

  if (itemLog.value) {
    itemLog.value.scrollTop = itemLog.value.scrollHeight;
  }
});

const Contagem = ref([0.1, 0.1, 0.1]);

const Contador = computed(() => Contagem.value);

const receivedLogs = ref([
  {
    message: "Carregando",
    message_type: "info",
  },
]);
const listLogs = computed(() => receivedLogs.value);
</script>

<template>
  <div>
    <BRow>
      <div class="col-6">
        <div class="card">
          <div class="card-header">
            <BButton variant="danger" @click="() => LogsSocket.emit('bot_stop', { pid: pid })">
              Parar Execução
            </BButton>
          </div>
          <div class="card-body p-5 bg-black overflow-y-auto" style="height: 37.5rem" ref="itemLog">
            <TransitionGroup tag="ul" name="fade">
              <li
                v-for="(item, index) in listLogs"
                :key="index"
                :id="String(index)"
                :class="item.message_type.toLowerCase()"
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
          </div>
          <div class="card-footer"></div>
        </div>
      </div>
      <div class="col-6">
        <div class="card">
          <div class="card-header"></div>
          <div
            class="card-body p-5 d-flex flex-column justify-content-center align-items-center"
            style="height: 37.5rem"
          >
            <Doughnut
              :options="{
                responsive: true,
              }"
              :data="{
                labels: ['EXECUTADOS', 'SUCESSOS', 'ERROS'],
                datasets: [
                  {
                    data: Contador,
                    backgroundColor: ['#0096C7', '#42cf06', '#FF0000'],
                  },
                ],
              }"
            >
            </Doughnut>
          </div>
          <div class="card-footer"></div>
        </div>
      </div>
    </BRow>
  </div>
</template>
<style lang="css" scoped>
.error {
  font-size: 1.3em;
  color: #bd0707;
  font-weight: bold;
}

.info {
  color: #f1b00b;
  font-size: 1.2em;
  font-weight: bold;
  font-family: "Times New Roman", Times, serif;
}

.warning {
  font-size: 1.2em;
  color: #af3f07;
  font-weight: bold;
}

.success {
  color: #11ab5b;
  font-size: 1.2em;
  font-weight: bold;
  font-family: "Times New Roman", Times, serif;
}

.log {
  font-size: 1.1em;
  color: #ffffffa8;
  font-weight: bold;
}
</style>
