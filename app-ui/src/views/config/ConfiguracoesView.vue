<script setup lang="ts">
import { api } from "@/controllers/axios";
import { useConfiguracoesStore } from "@/stores/config";
import { useMessageStore } from "@/stores/message";
import { isAxiosError } from "axios";
import DataTablesCore from "datatables.net-bs5";
import DataTable from "datatables.net-vue3";
import { storeToRefs } from "pinia";
import { onBeforeMount, ref } from "vue";
import { useRouter } from "vue-router";
DataTable.use(DataTablesCore);

const data = ref([["-", "-", "-", "-", "-", "-", "-"]]);
const overlayFormSubmit = ref(false);
const router = useRouter();
const { message } = storeToRefs(useMessageStore());
const { UsersList } = storeToRefs(useConfiguracoesStore());
onBeforeMount(async () => {
  try {
    const response: ResponseUsers = await api.get("/usuarios/lista");
    if (response.data && response.data.database) {
      UsersList.value = response.data.database;
    }
  } catch {
    //
  }
  if (UsersList.value) {
    data.value = [];
    Array.from(UsersList.value).map((item) => {
      const temp_data = [
        item.id,
        item.login,
        item.nome_usuario,
        item.email,
        item.login_time,
        item.login_id,
      ];
      data.value.push(temp_data);
    });
  }
});

async function deleteUser(user_id: string) {
  let msg = "Erro ao salvar usuário";
  let success = false;

  try {
    const Form = new FormData();

    Form.append("id", user_id);
    Form.append("method_request", "DELETE");

    const resp = await api.post("/perform_user", Form);

    msg = resp.data.message;
    success = true;
  } catch (err) {
    if (
      isAxiosError(err) &&
      err.response &&
      err.response.data &&
      (err.response.data.message || err.response.data.description)
    ) {
      msg = err.response.data.message || err.response.data.description;
    }
  }

  message.value = msg;
  if (success) {
    router.push({ name: "dashboard" });
  }
  overlayFormSubmit.value = false;
}
document.title = "CrawJUD - Config. Usuários";
</script>
<template>
  <div class="container mt-4 mb-3">
    <div class="card-header mb-3">
      <h1 class="mb-3">Usuários</h1>
      <hr />
      <div class="d-flex gap-2">
        <RouterLink
          :to="{ name: 'newUser', params: { metodo: 'cadastro' } }"
          class="btn btn-icon-split btn-success mb-3"
        >
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
            <BOverlay :show="overlayFormSubmit" rounded="sm" opacity="0.3">
              <DataTable
                :data="data"
                class="table table-striped"
                :options="{ pageLength: 5, ordering: true, lengthMenu: [5] }"
              >
                <thead>
                  <tr>
                    <th class="fw-semibold">#</th>
                    <th>Login</th>
                    <th>Nome Usuário</th>
                    <th>E-mail</th>
                    <th>Último Login</th>
                    <th>ID Login</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tfoot>
                  <tr>
                    <th class="fw-semibold">#</th>
                    <th>Login</th>
                    <th>Nome Usuário</th>
                    <th>E-mail</th>
                    <th>Último Login</th>
                    <th>ID Login</th>
                    <th>Ações</th>
                  </tr>
                </tfoot>
                <template #column-6="props">
                  <div class="d-flex gap-1">
                    <button class="btn btn-warning btn-sm">Editar</button>
                    <button class="btn btn-danger btn-sm" @click="deleteUser(props.rowData[0])">
                      Deletar
                    </button>
                  </div>
                </template>
              </DataTable>
            </BOverlay>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
