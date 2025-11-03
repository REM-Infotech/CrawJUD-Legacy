<script setup lang="ts">
import { Doughnut } from "vue-chartjs";
const chartData = ref([40, 20, 12]);

const LogsSocket = socketio.socket("/bot_logs");

onMounted(() => {
  const route = useRoute();
  console.log(route.name);
  const pid_param: string = route.params.pid as string;
  let pid;

  if (pid_param) {
    pid = pid_param;
    sessionStorage.setItem("pid", pid);
  } else if (!pid_param) {
    pid = sessionStorage.getItem("pid") as string;
  }

  LogsSocket.connect();
  LogsSocket.emit("join_room", { room: pid });
});

LogsSocket.on("logbot", (data) => {
  console.log(data);
  receivedLogs.value.push(data);
});

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
          <div class="card-header"></div>
          <div class="card-body p-5 bg-black overflow-y-auto" style="height: 37.5rem">
            <TransitionGroup tag="ul" name="fade" ref="itemLog">
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
                    data: chartData,
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
</style>
