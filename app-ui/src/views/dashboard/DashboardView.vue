<script setup lang="ts">
import { api } from "@/controllers/axios";
import router from "@/router";
import DataTablesCore from "datatables.net-bs5";
import DataTable from "datatables.net-vue3";
import { onBeforeMount, onMounted, ref } from "vue";
DataTable.use(DataTablesCore);

const beta_teste = import.meta.env.VITE_BETA_TEST;
const data = ref<string[][]>([]);
const ModalAviso = ref(false);
onBeforeMount(async () => {
  try {
    const resp: ExecutionsResponse = await api.request({ method: "GET", url: "/executions" });

    if (resp.data.data) {
      const execut_data = resp.data.data;
      Array.from(execut_data).map((value) => {
        const temp_list: string[] = [];
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        Object.entries(value).map(([_, value]) => {
          temp_list.push(value);
        });

        data.value.push(temp_list);
      });
    }
  } catch {
    //
  }
});

/**
 * Navega para uma rota específica usando nome e parâmetros.
 *
 * @param {{ name: string, params: { pid: string } }} route - Objeto contendo o nome da rota e parâmetros.
 * @returns {void} Não retorna valor.
 */
function pushLogsBotRoute(pid: string): void {
  router.push({ name: "logs_execution", params: { pid: pid } });
}

onMounted(() => {
  if (beta_teste) {
    ModalAviso.value = true;
  }
});

document.title = "CrawJUD - Dashboard";
</script>

<template>
  <div class="container">
    <h1 class="">Dashboard</h1>
    <ol class="breadcrumb mb-4">
      <li class="breadcrumb-item active">Dashboard</li>
    </ol>
    <div class="card mb-4">
      <div class="card-header">
        <i class="fas fa-table me-1"></i>
        Execuções
      </div>
      <div class="card-body">
        <DataTable
          :data="data"
          class="table table-striped"
          :options="{ pageLength: 5, ordering: true, lengthMenu: [5] }"
        >
          <thead>
            <tr>
              <th>Robô</th>
              <th>Status Arquivo</th>
              <th>PID</th>
              <th>Data Inicio</th>
              <th>Status Execução</th>
              <th>Data Fim</th>
            </tr>
          </thead>
          <tfoot>
            <tr>
              <th>Robô</th>
              <th>Status Arquivo</th>
              <th>PID</th>
              <th>Data Inicio</th>
              <th>Status Execução</th>
              <th>Data Fim</th>
            </tr>
          </tfoot>
          <template #column-2="props">
            <div class="d-flex gap-1">
              <a
                href="#"
                v-if="props.rowData[4] == 'Em Execução'"
                @click="pushLogsBotRoute(String(props.cellData))"
              >
                {{ props.cellData.slice(0, 8).toUpperCase() }}
              </a>
              <span v-else>
                {{ props.cellData.slice(0, 8).toUpperCase() }}
              </span>
            </div>
          </template>
        </DataTable>
      </div>
    </div>
    <BModal v-model="ModalAviso" id="modal-center" centered title="Aviso Importante" ok-only>
      <p class="my-4">Aviso!</p>
      <p>Essa é uma versão de testes, erros podem acontecer</p>
      <p>Caso ocorra algum erro, realizar execução na versão antiga e reportar ao administrador</p>
    </BModal>
  </div>
</template>
