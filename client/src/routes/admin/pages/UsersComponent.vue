<script setup lang="ts">
import { onBeforeMount, ref } from "vue";
import { api } from "../../../main";
import { faPen, faTrash, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import DataTable from "datatables.net-vue3";
import DataTablesCore from "datatables.net-bs5";
import { current_action, form } from "../resources/formusr";
import { submitForm, delete_call } from "../resources/formusr";
const items = ref();

const submitDelete = () => {
  delete_call.value = true;
  submitForm(new Event("submit"));
};

DataTable.use(DataTablesCore);
onBeforeMount(async () => {
  try {
    const response = await api.get("/users");

    items.value = response.data.database.map((item) => {
      return [item.id, item.login, item.nome_usuario, item.email];
    });
  } catch {
    //
  }
});

function setupEdit(item) {
  form.id = item[0];
  form.name = item[1];
  form.login = item[2];
  form.email = item[3];
  current_action.value = "Editar Usuário";
}
</script>

<template>
  <div class="card" data-bs-theme="dark">
    <div class="card-header d-grid gap-3">
      <div class="d-flex gap-3 p-2">
        <div class="justify-content-xxl-end align-middle me-auto text-center">
          <h3>Usuários</h3>
        </div>
        <div class="justify-content-xxl-end">
          <BButton
            class="btn me-2 fw-bold"
            v-b-modal.ModalFormUsr
            variant="outline-success"
            @click="current_action = 'Cadastrar Usuário'"
          >
            <span>
              <FontAwesomeIcon :icon="faPlus" class="me-2" />
            </span>
            <em>Cadastrar Usuário</em>
          </BButton>
          <!-- <button type="button" class="btn btn-outline-warning me-2 fw-bold">
            Encerrar Execução<em>Cadastrar Usuário</em>
          </button> -->
        </div>
      </div>
    </div>
    <div class="card-body table-responsive">
      <DataTable :data="items" class="placeholder-glow table table-striped table-hover">
        <thead>
          <tr>
            <th>#</th>
            <th>Login</th>
            <th>Nome</th>
            <th>E-mail</th>
            <th data-sortable="false">Ações</th>
          </tr>
        </thead>
        <template #column-4="props">
          <div class="d-flex justify-content-md-start">
            <BButton
              size="sm"
              class="me-2"
              variant="outline-warning"
              @click="setupEdit(props.rowData)"
              v-b-modal.ModalFormUsr
            >
              <span>
                <FontAwesomeIcon :icon="faPen" class="me-2" />
              </span>
              <em>Editar</em>
            </BButton>
            <BButton
              class="me-2"
              size="sm"
              variant="outline-danger"
              @click="submitDelete"
              v-b-modal.ModalFormUsr
            >
              <span>
                <FontAwesomeIcon :icon="faTrash" class="me-2" />
              </span>
              <em>Deletar</em>
            </BButton>
          </div>
        </template>
        <tfoot>
          <tr>
            <th>#</th>
            <th>Login</th>
            <th>Nome</th>
            <th>E-mail</th>
            <th data-sortable="false">Ações</th>
          </tr>
        </tfoot>
      </DataTable>
    </div>
  </div>
</template>
