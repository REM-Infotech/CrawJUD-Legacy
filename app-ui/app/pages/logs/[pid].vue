<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import { Doughnut } from "vue-chartjs";

const LogsSocket = socketio.socket("/bot_logs");

const itemLog = ref<HTMLElement | null>(null); // Ref para o ul
const pid = ref("");
const link_arquivo = ref("");
const listLogs = computed(() => receivedLogs.value);

const Contagem: Record<keyof ValoresContador, number> = reactive({
  total: 0,
  sucessos: 0,
  erros: 0,
  restantes: 0,
});
const Contador = computed(() => [Contagem.restantes, Contagem.sucessos, Contagem.erros]);
const receivedLogs = ref([
  {
    message: "Carregando",
    message_type: "info",
  },
]);

onMounted(() => {
  const route = useRoute();
  const pid_param: string = route.params.pid as string;

  if (pid_param) {
    pid.value = pid_param;
    sessionStorage.setItem("pid", pid.value);
  } else if (!pid_param) {
    pid.value = sessionStorage.getItem("pid") as string;
  }

  LogsSocket.connect();
  LogsSocket.emit("join_room", { room: pid.value });
});

LogsSocket.on("logbot", async (data: Message) => {
  receivedLogs.value.push(data);
  await nextTick();
  Object.entries(Contagem).forEach(([key, _]) => {
    if (key as keyof ValoresContador) {
      Contagem[key as keyof ValoresContador] = data[key as keyof ValoresContador];
    }
  });

  if (data.link) {
    link_arquivo.value = data.link;
  }

  if (itemLog.value) {
    itemLog.value.scrollTop = itemLog.value.scrollHeight;
  }
});
</script>

<template>
  <div class="card">
    <div class="card-header">
      <div class="d-flex">
        <BButton variant="danger" @click="() => LogsSocket.emit('bot_stop', { pid: pid })">
          Parar Execução
        </BButton>
        <a v-if="link_arquivo" class="btn btn-danger" :href="link_arquivo"> Baixar Arquivo </a>
      </div>
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
              <span class="fw-semibold">
                Logs Execução: <strong>{{ pid }}</strong>
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
      <span> Total: {{ Contagem.total }}</span>
      <span> Sucessos: {{ Contagem.sucessos }}</span>
      <span> Erros: {{ Contagem.erros }}</span>
      <span> Restantes: {{ Contagem.restantes }}</span>
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
