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

  Contagem.value = [data.remaining_count, data.success_count, data.error_count];
  await nextTick();

  contador_reativo.total = data.total;
  contador_reativo.sucessos = data.success_count;
  contador_reativo.erros = data.error_count;
  contador_reativo.restantes = data.remaining_count;

  if (itemLog.value) {
    itemLog.value.scrollTop = itemLog.value.scrollHeight;
  }
});

const Contagem = ref([0.1, 0.1, 0.1]);

const contador_reativo = reactive({
  total: 0,
  sucessos: 0,
  erros: 0,
  restantes: 0,
});

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
  <div class="card">
    <div class="card-header">
      <BButton variant="danger" @click="() => LogsSocket.emit('bot_stop', { pid: pid })">
        Parar Execução
      </BButton>
    </div>
    <div class="card-body">
      <BRow>
        <div class="col-6">
          <div class="card">
            <div class="card-header">
              <span class="fw-semibold"
                >Logs Execução: <strong>{{ pid }}</strong>
              </span>
            </div>
            <div
              class="card-body p-5 bg-black overflow-y-auto"
              style="height: 37.5rem"
              ref="itemLog"
            >
              <TransitionGroup tag="ul" name="fade">
                <li
                  v-for="(item, index) in listLogs"
                  :key="index"
                  :id="String(index)"
                  :class="item.message_type.toLowerCase()"
                >
                  <span class="fw-bold">
                    {{ item.message }}
                  </span>
                </li>
              </TransitionGroup>
            </div>
          </div>
        </div>
        <div class="col-6">
          <div class="card">
            <div class="card-header">
              <span class="fw-semibold"
                >Logs Execução: <strong>{{ pid }}</strong>
              </span>
            </div>
            <div
              class="card-body p-5 d-flex flex-column justify-content-center align-items-center"
              style="height: 37.5rem"
            >
              <Doughnut
                :options="{
                  responsive: true,
                }"
                :data="{
                  labels: ['PENDENTES', 'SUCESSOS', 'ERROS'],
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
          </div>
        </div>
      </BRow>
    </div>
    <div class="card-footer">
      <span> Total: {{ contador_reativo.total }}</span>
      <span> Sucessos: {{ contador_reativo.sucessos }}</span>
      <span> Erros: {{ contador_reativo.erros }}</span>
      <span> Restantes: {{ contador_reativo.restantes }}</span>
    </div>
  </div>
</template>
<style lang="css" scoped>
.error {
  color: #bd0707;
  font-weight: bold;
}

.info {
  color: #f1b00b;
  font-weight: bold;
  font-family: "Times New Roman", Times, serif;
}

.warning {
  color: #af3f07;
  font-weight: bold;
}

.success {
  color: #66e96d;
  font-weight: bold;
  text-decoration: underline wavy green 1px !important;
  font-family: "Times New Roman", Times, serif;
}

.log {
  color: #a146eb;
  font-weight: bold;
}
</style>
