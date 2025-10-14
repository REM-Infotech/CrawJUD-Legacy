<script setup lang="ts">
import { api } from "@/res/axios";
import { useCredentialsStore } from "@/stores/credentials";
import DataTablesCore from "datatables.net-bs5";
import DataTable from "datatables.net-vue3";
import { storeToRefs } from "pinia";
import { onBeforeMount, ref } from "vue";
import { RouterLink } from "vue-router";
DataTable.use(DataTablesCore);

const data = ref<(string | number)[][]>([]);
const { credentialsList } = storeToRefs(useCredentialsStore());
onBeforeMount(async () => {
  try {
    const response: ResponseCredentials = await api.get("/credentials");
    if (response.data && response.data.database) {
      credentialsList.value = response.data.database;
    }
  } catch {
    //
  }
  if (credentialsList.value) {
    Array.from(credentialsList.value).map((item) => {
      const temp_data = [item.id, item.nome_credencial, item.system, item.login_method];
      data.value.push(temp_data);
    });
  }
});

document.title = "CrawJUD - Credenciais";
</script>

<template>
  <div class="container mt-4 mb-3">
    <div class="card-header mb-3">
      <h1 class="mb-3">Credenciais</h1>
      <hr />
      <div class="d-flex gap-2">
        <RouterLink :to="{ name: 'newCredential' }" class="btn btn-icon-split btn-success mb-3">
          <span class="text">Cadastrar</span>
        </RouterLink>
        <button
          type="button"
          data-bs-toggle="modal"
          class="btn btn-icon-split btn-warning mb-3"
          data-bs-target="#importarquivo"
        >
          <span class="text">Import em lotes</span>
        </button>
        <a href="#" class="btn btn-icon-split btn-primary mb-3">
          <span class="text">Gerar Relatório</span>
        </a>
      </div>
    </div>
    <div class="card-body">
      <div class="row g-3">
        <hr />
        <div class="col-md-12">
          <div class="table-responsive mb-3 bg-body-tertiary p-3 rounded rounded-4">
            <DataTable :data="data" class="table table-striped">
              <thead>
                <tr>
                  <th class="fw-bold">#</th>
                  <th>Nome Credencial</th>
                  <th>Portal</th>
                  <th>Método Login</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tfoot>
                <tr>
                  <th class="fw-bold">#</th>
                  <th>Nome Credencial</th>
                  <th>Portal</th>
                  <th>Método Login</th>
                  <th>Ações</th>
                </tr>
              </tfoot>
              <template #column-4>
                <div class="d-flex gap-1">
                  <button class="btn btn-warning btn-sm">Editar</button>
                  <button class="btn btn-danger btn-sm">Deletar</button>
                </div>
              </template>
            </DataTable>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
