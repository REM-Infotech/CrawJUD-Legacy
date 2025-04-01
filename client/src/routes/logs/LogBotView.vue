<script setup lang="ts">
import { io as socketio } from "socket.io-client";
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Chart, ChartType } from "chart.js/auto";
import ChartProgress from "./components/ChartProgress.vue";
import NavBarComponent from "../../components/NavBarComponent.vue";
import SideBarComponent from "../../components/SideBarComponent.vue";
const { show: show_message } = useModal("ModalMessage");
import { $, api } from "../../main";
import { useModal } from "bootstrap-vue-next";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { onBeforeMount } from "vue";
import LogsView from "./components/LogsView.vue";
import { AxiosError, AxiosResponse } from "axios";

const route = useRoute();
const router = useRouter();
const pid = route.params.pid as string;
let Pages;
const percent_progress = document.getElementById("progress_info");
const io = socketio("https://api.reminfotech.net.br/log", {
  extraHeaders: {
    pid: pid,
  },
});
let LogsBotChart: Chart | null = null;
const colors_message = {
  info: "orange",
  error: "RED",
  log: "#d3e3f5",
  success: "#42cf06",
};

// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.font.family =
  '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.color = "#292b2c";

onMounted(() => {
  const ctx = (document.getElementById("LogsBotChart") as HTMLCanvasElement)?.getContext("2d");
  if (!ctx) return;
  LogsBotChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["RESTANTES", "SUCESSOS", "ERROS"],
      datasets: [
        {
          data: [0.1, 0.1, 0.1],
          backgroundColor: ["#0096C7", "#42cf06", "#FF0000"],
        },
      ],
    },
  });

  api
    .get(`/get_execution/${pid}`)
    .then((response: AxiosResponse) => {
      if (response.status === 200) {
        const url = response.data.document_url as string;
        $("#download-button").removeClass("disabled");
        $("#download-button").removeClass("btn-outline-success");
        $("#download-button").addClass("btn-success");
        $("#download-button").attr("href", url);
      }
    })
    .catch((error: AxiosError) => {
      const response = error.response;

      if (response?.status === 404) {
        //
      } else if (response?.status === 401 || response?.status === 422) {
        $("#message").text("É necessário fazer login para acessar esta página");
        router.push({ name: "login" });

        setTimeout(() => {
          show_message();
        }, 500);
      } else {
        // console.log(error);
      }
    });

  if (!$("#download-button").hasClass("disabled")) {
    $("#message").text(`Execução iniciada! PID: ${pid}`);
    show_message();
  }
});

try {
  io.on("error", () => {});

  io.on("disconnect", () => {
    // console.log("Disconnected from crawjud");
  });
  io.on("connect", function () {
    io.emit("join", { pid: pid });
    // console.log("Connected to crawjud");
  });

  io.on("join", () => {
    // console.log("Joinned!");
  });

  io.on("log_message", function (data) {
    var messagePid = data.pid;

    function updateElements(data) {
      var typeLog = String(data.type);
      var total = parseInt(data.total);
      var remaining = parseInt(data.remaining);
      var success = parseInt(data.success);
      var errors = parseInt(data.errors);
      var status = data.status;
      var executed = success + errors;

      if (
        Number.isNaN(total) ||
        Number.isNaN(remaining) ||
        Number.isNaN(success) ||
        Number.isNaN(errors)
      ) {
        return;
      }

      var CountErrors = document.querySelector('span[id="errors"]') as HTMLElement;
      var Countremaining = document.querySelector('span[id="remaining"]') as HTMLElement;
      var CountSuccess = document.querySelector('span[id="success"]') as HTMLElement;
      var TextStatus = document.querySelector('span[id="status"]') as HTMLElement;
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      var lastRemainign = LogsBotChart
        ? parseInt(String(LogsBotChart.data.datasets[0].data[0] ?? 0))
        : 0;

      if (typeLog === "info") {
        Pages = Pages + 1;
        // console.log(typeLog);
      }

      if (remaining < 0) {
        remaining = 0;
      }

      if (remaining === 0) {
        remaining = Pages;
      }

      CountErrors.innerHTML = `Erros: ${errors}`;
      Countremaining.innerHTML = `Restantes: ${remaining}`;
      TextStatus.innerHTML = `Status: ${status} | Total: ${total}`;

      var progress = (executed / total) * 100;
      var textNode = document.createTextNode(progress.toFixed(2) + "%");

      if (!LogsBotChart) return;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const chartType: ChartType = (LogsBotChart.config as any).type;
      var grafMode = data.graphicMode;

      if (status !== "Finalizado") {
        CountSuccess.innerHTML = `Sucessos: ${success}`;
        LogsBotChart.data.datasets[0].data = [remaining, success, errors];
      }

      if (grafMode !== undefined && grafMode !== chartType) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (LogsBotChart.config as any).type = grafMode;
        // eslint-disable-next-line @typescript-eslint/no-unused-expressions
        LogsBotChart.data.datasets[0].data;
        if (LogsBotChart.data.labels && Array.isArray(LogsBotChart.data.labels)) {
          LogsBotChart.data.labels[0] = "PÁGINAS";
        }
        Countremaining.innerHTML = `Páginas: ${remaining}`;
      }

      if (parseInt(data.remaining) > 0 && percent_progress) {
        percent_progress.innerHTML = "";
        percent_progress.appendChild(textNode);
        percent_progress.style.width = progress + "%";
      }

      LogsBotChart.update();
    }

    if (messagePid == pid) {
      const randomId = `id_${Math.random().toString(36).substring(2, 9)}`;
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const pos: number = parseInt(data.pos);
      const message: string = data.message;
      var typeLog: string = data.type;
      const ul_messages = $("#messages");
      ul_messages.append(
        `<li id="${randomId}" class="fw-bold" style="color: ${colors_message[typeLog]}">${message}</li>`,
      );

      setTimeout(() => {
        updateElements(data);
        document.getElementById(randomId)?.scrollIntoView({ behavior: "smooth", block: "end" });
      }, 500);

      if (message.toLowerCase().includes("fim da execução")) {
        api
          .get(`/get_execution/${pid}`)
          .then((response: AxiosResponse) => {
            if (response.status === 200) {
              const url = response.data.document_url as string;
              $("#download-button").removeClass("disabled");
              $("#download-button").removeClass("btn-outline-success");
              $("#download-button").addClass("btn-success");
              $("#download-button").attr("href", url);
            }
          })
          .catch(() => {
            router.push({ name: "login" });
          });
      }
    }
  });
} catch {
  // console.log(error);
}

const stop_execut = () => {
  io.emit("terminate_bot", { pid: pid });
  const ul_messages = $("#messages");

  const randomId = `id_${Math.random().toString(36).substring(2, 9)}`;

  ul_messages.append(
    `<li id=${randomId} class="fw-bold" style="color: ${colors_message["info"]}">Parando execução</li>`,
  );

  setTimeout(() => {
    document.getElementById(randomId)?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, 500);
};
</script>

<template>
  <NavBarComponent />
  <div id="content" class="mt-4 mb-4">
    <SideBarComponent />
    <div>
      <main>
        <BContainer fluid class="px-4">
          <div class="card">
            <div class="card-header">
              <div class="d-flex gap-3">
                <div class="justify-content-xxl-end align-middle me-auto text-center">
                  <h4>Estatisticas</h4>
                </div>
                <div class="justify-content-xxl-end">
                  <a
                    class="btn btn-outline-success disabled me-2"
                    aria-disabled="true"
                    id="download-button"
                    href="#"
                    >Baixar Documento</a
                  >
                  <button type="button" class="btn btn-warning" @click="stop_execut()">
                    Encerrar Execução
                  </button>
                </div>
              </div>
            </div>
            <div class="card-body bg-warning">
              <div class="row">
                <div class="col-xl-6 col-md-6">
                  <LogsView />
                </div>
                <div class="col-xl-6 col-md-6">
                  <ChartProgress />
                </div>
              </div>
            </div>
            <div class="card-footer bg-secondary">
              <div class="container-fluid mt-2 mb-2">
                <div
                  id="progress_bar"
                  class="progress"
                  role="progressbar"
                  aria-label="Info example"
                  aria-valuenow="0"
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
                  <div
                    id="progress_info"
                    class="progress-bar bg-info text-dark"
                    style="width: 0%"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </BContainer>
      </main>
    </div>
  </div>
</template>

<style>
.inner-scroll {
  overflow-y: hidden !important;
}
</style>
