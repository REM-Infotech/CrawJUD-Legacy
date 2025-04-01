<script setup lang="ts">
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { onBeforeMount, onMounted, ref } from "vue";
import DataTable from "datatables.net-vue3";
import DataTablesCore from "datatables.net-bs5";
import { useRouter } from "vue-router";
import { useModal } from "bootstrap-vue-next";
import { convertDate } from "../services/convert_date";
DataTable.use(DataTablesCore);

const options = {
  language: {
    url: "//cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json",
  },
};
const { show: show_load, hide: hide_load } = useModal("modal-load");
const { show: show_message } = useModal("ModalMessage");

let items = [];
import { $, api } from "../main";
import { faDownload, faEye } from "@fortawesome/free-solid-svg-icons";

const data_ = ref(false);
const router = useRouter();
onMounted(async function () {
  api
    .get("/executions", {
      withXSRFToken: true,
      withCredentials: true,
      xsrfCookieName: "access_token_cookie",
      xsrfHeaderName: "X-CSRF-TOKEN",
    })
    .then(async (response) => {
      items = response.data.data.map((item) => {
        return [
          item.pid,
          item.user,
          item.botname,
          item.xlsx,
          () => {
            return convertDate(item.start_date);
          },
          item.status,

          () => {
            return convertDate(item.stop_date);
          },
          item.file_output,
        ];
      });
      data_.value = true;
    })
    .catch((error) => {
      if (error.code === "ERR_NETWORK") {
        $("#message").text("Erro de conexão com o servidor, tente novamente mais tarde.");
        show_message();
        router.push({ name: "login" });
      } else if (error.code) {
        if (error.status === 401) {
          // console.log(error);
          sessionStorage.setItem("message", "Sessão expirada, faça login novamente!");
          router.push({ name: "login" });
        }
        // console.log(error);
      }
    });
});

const download_file = async (file: string) => {
  show_load();

  setTimeout(async () => {
    api
      .get(`/executions/download/${file}`)
      .then((response) => {
        const data = response.data;
        const url: string = data.url;
        window.open(url, "_blank");

        setTimeout(() => {
          hide_load();
        }, 500);

        $("#message").text(`Download do arquivo "${file}" iniciado!`);
        show_message();
      })
      .catch((response) => {
        // check if response is 4** error and not 404

        if (response.response.status === 401 || response.response.status === 422) {
          $("#message").text("É necessário estar autenticado para acessar essa página.");
          router.push({ name: "login" });
          show_message();
        }
      });
  }, 1000);
};
</script>

<template>
  <div data-bs-theme="dark" class="card mb-4">
    <div class="card-header">
      <i class="fas fa-table me-1"></i>
      Execuções
    </div>
    <div class="card-body">
      <div v-if="data_" class="table-responsive">
        <DataTable
          :data="items"
          class="placeholder-glow table table-striped table-hover"
          :options="options"
        >
          <thead>
            <tr>
              <th>#</th>
              <th>Usuário</th>
              <th>Nome do Robô</th>
              <th>Arquivo de Execução</th>
              <th>Data da Execução</th>
              <th>Status</th>
              <th>Data finalização</th>
              <th data-sortable="false">Arquivo de saida</th>
            </tr>
          </thead>
          <template #column-7="props">
            <button
              v-if="props.rowData[5].toString().toLowerCase() !== 'em execução'"
              class="btn btn-sm btn-success"
              data-bs-toggle="tooltip"
              data-bs-title="Default tooltip"
              @click="download_file(props.cellData)"
            >
              <FontAwesomeIcon :icon="faDownload" />
            </button>

            <a
              v-else-if="props.rowData[5].toString().toLowerCase() === 'em execução'"
              :href="`/logs_bot/${props.rowData[0]}`"
              class="btn btn-sm btn-primary"
              data-bs-toggle="tooltip"
              data-bs-title="Default tooltip"
              ><FontAwesomeIcon :icon="faEye"
            /></a>
          </template>
          <tfoot>
            <tr>
              <th>#</th>
              <th>Usuário</th>
              <th>Nome do Robô</th>
              <th>Arquivo de Execução</th>
              <th>Data da Execução</th>
              <th>Status</th>
              <th>Data finalização</th>
              <th data-sortable="false">Arquivo de saida</th>
            </tr>
          </tfoot>
        </DataTable>
      </div>
      <div v-if="!data_" class="table-responsive">
        <table class="placeholder-glow table table-striped table-hover">
          <thead>
            <tr>
              <th>#</th>
              <th>Usuário</th>
              <th>Nome do Robô</th>
              <th>Arquivo de Execução</th>
              <th>Data da Execução</th>
              <th>Status</th>
              <th>Data finalização</th>
              <th data-sortable="false">Arquivo de saida</th>
            </tr>
          </thead>
          <tbody>
            <tr class="text-center">
              <td colspan="8"><span class="placeholder w-100 rounded">Carregando</span></td>
            </tr>
            <tr class="text-center">
              <td colspan="8"><span class="placeholder w-100 rounded">Carregando</span></td>
            </tr>
            <tr class="text-center">
              <td colspan="8"><span class="placeholder w-100 rounded">Carregando</span></td>
            </tr>
            <tr class="text-center">
              <td colspan="8"><span class="placeholder w-100 rounded">Carregando</span></td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <th>#</th>
              <th>Usuário</th>
              <th>Nome do Robô</th>
              <th>Arquivo de Execução</th>
              <th>Data da Execução</th>
              <th>Status</th>
              <th>Data finalização</th>
              <th data-sortable="false">Arquivo de saida</th>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>
