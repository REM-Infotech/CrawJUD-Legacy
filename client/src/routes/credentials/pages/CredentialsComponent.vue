<script setup lang="ts">
import { onBeforeMount, ref } from "vue";
import { $, api } from "../../../main";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { faPen, faTrash, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import DataTable from "datatables.net-vue3";
import DataTablesCore from "datatables.net-bs5";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { current_action, form } from "../resources/formcred";
import { delete_call } from "../resources/formcred";
import { AxiosResponse } from "axios";
import { useModal } from "bootstrap-vue-next";
const items = ref();

const { show: show_message } = useModal("ModalMessage");

const submitDelete = (id: number) => {
  delete_call.value = true;

  const formData = new FormData();

  formData.append("id", id.toString());
  formData.append("action", "delete");

  api
    .post("/peform_credencial", formData, {
      withXSRFToken: true,
      withCredentials: true,
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "x-csrf-token": sessionStorage.getItem("x-csrf-token") || "",
      },
    })
    .then((response: AxiosResponse) => {
      $("#message").text(response.data.message);

      show_message();
    })
    .finally(() => {
      delete_call.value = false;
    });
};

DataTable.use(DataTablesCore);
onBeforeMount(async () => {
  try {
    const response = await api.get("/credentials");

    items.value = response.data.database.map((item) => {
      return [item.id, item.credential, item.system, item.login_method];
    });
  } catch {
    //
  }
});

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function setupEdit(item) {
  console.log(item);
  // form.id = item[0];
  // form.name = item[1];
  // form.login = item[2];
  // form.email = item[3];
  // current_action.value = "Editar Usuário";
}
</script>

<template>
  <div class="card" data-bs-theme="dark">
    <div class="card-header d-grid gap-3">
      <div class="d-flex gap-3 p-2">
        <div class="justify-content-xxl-end align-middle me-auto text-center"></div>
        <div class="justify-content-xxl-end">
          <div class="dropdown">
            <BButton
              class="btn me-2 fw-bold dropdown-toggle"
              variant="outline-success"
              @click="current_action = 'Cadastrar Usuário'"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <span>
                <FontAwesomeIcon :icon="faPlus" class="me-2" />
              </span>
              <em>Cadastrar Credencial</em>
            </BButton>
            <ul class="dropdown-menu mt-2 ms-5">
              <li>
                <a class="dropdown-item" href="#" v-b-modal.ModalFormUsr>
                  <em>Usuário/Senha</em>
                </a>
              </li>
              <li>
                <a class="dropdown-item" href="#">
                  <em>Certificado Digital</em>
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="card-body table-responsive">
      <DataTable :data="items" class="placeholder-glow table table-striped table-hover">
        <thead>
          <tr>
            <th>#</th>
            <th>Nome Credencial</th>
            <th>Sistema</th>
            <th>Método Login</th>
            <th data-sortable="false">Ações</th>
          </tr>
        </thead>
        <template #column-4="props">
          <div class="d-flex justify-content-md-start">
            <!-- <BButton
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
            </BButton> -->
            <BButton
              class="me-2"
              size="sm"
              variant="outline-danger"
              @click="submitDelete(props.rowData[0])"
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
            <th>Nome Credencial</th>
            <th>Sistema</th>
            <th>Método Login</th>
            <th data-sortable="false">Ações</th>
          </tr>
        </tfoot>
      </DataTable>
    </div>
  </div>
</template>
