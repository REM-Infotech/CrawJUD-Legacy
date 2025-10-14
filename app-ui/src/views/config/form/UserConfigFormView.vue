<script setup lang="ts">
import { api } from "@/res/axios";

import { useMessageStore } from "@/stores/message";
import { isAxiosError } from "axios";
import { storeToRefs } from "pinia";
import { computed, onBeforeMount, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const showPasword = ref(false);
const overlayFormSubmit = ref(false);

const { message } = storeToRefs(useMessageStore());
const route = useRoute();
const router = useRouter();

onBeforeMount(() => {
  const metodo_form = route.params.metodo;

  Form.method_request = TranslatedMethods[String(metodo_form)];
});

const Form = reactive({
  method_request: "",
  login: "",
  nome_usuario: "",
  email: "",
  password: "",
});

/**
 * Valida os campos obrigatórios do formulário de usuário.
 *
 * @param {{ [key: string]: string }} form - Objeto com os dados do formulário.
 * @returns {string | null} Mensagem de erro ou null se válido.
 */
function validateUserForm(form: { [key: string]: string }): string | null {
  const requiredFields = [
    { key: "nome_usuario", message: "É necessário informar o nome do usuário!" },
    { key: "login", message: "Informe um login para o usuário!" },
    { key: "email", message: "Informe um email para o usuário!" },
    { key: "password", message: "Informe uma senha para o usuário!" },
  ];

  for (const field of requiredFields) {
    if (!form[field.key]) {
      return field.message;
    }
  }
  return null;
}

const TranslatedMethods: { [key: string]: string } = {
  cadastro: "INSERT",
  editar: "UPDATE",
};

const TypeInputPassword = computed(() => (showPasword.value ? "text" : "password"));
async function handleSubmit(e: Event) {
  e.preventDefault();
  overlayFormSubmit.value = true;
  const error = validateUserForm(Form);
  if (error) {
    message.value = error;
    overlayFormSubmit.value = false;
    return;
  }
  let msg = "Erro ao salvar usuário";
  let success = false;
  try {
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
    router.push({ name: "configuracoes" });
  }
  overlayFormSubmit.value = false;
}
</script>

<template>
  <div class="container px-4">
    <BOverlay :show="overlayFormSubmit" rounded="sm" opacity="0.3">
      <form id="Form" class="card border-0 shadow rounded-3 my-5" @submit="handleSubmit">
        <h4 class="card-header p-4">Cadastro Usuário</h4>
        <div class="card-body bg-opacity-75 p-4 p-sm-5">
          <div class="row g-3 rounded justify-content-center p-3">
            <div
              class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary"
            >
              <BFormGroup
                id="fieldset-name"
                label="Nome do Usuário"
                label-for="name"
                label-class="mb-1"
              >
                <BFormInput
                  type="text"
                  id="name"
                  v-model="Form.nome_usuario"
                  placeholder="João da Silva"
                  trim
                />
              </BFormGroup>
            </div>
            <div
              class="col-md-5 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary"
            >
              <BFormGroup
                id="fieldset-usuário"
                label="Usuário"
                label-for="usuario"
                label-class="mb-1"
              >
                <BFormInput
                  type="text"
                  id="usuario"
                  name="usuario_"
                  v-model="Form.login"
                  placeholder="joao.silva"
                  trim
                />
              </BFormGroup>
            </div>
            <div
              class="col-md-5 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary"
            >
              <BFormGroup id="fieldset-email" label="E-Mail" label-for="email" label-class="mb-1">
                <BFormInput
                  type="email"
                  id="email"
                  placeholder="email@example.com"
                  v-model="Form.email"
                  trim
                />
              </BFormGroup>
            </div>
            <div
              class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary"
            >
              <BFormGroup id="fieldset-password" label="Senha" label-for="senha" label-class="mb-3">
                <BFormInput
                  :type="TypeInputPassword"
                  id="senha"
                  name="senha_"
                  placeholder="Senha para o usuário"
                  v-model="Form.password"
                  trim
                />
              </BFormGroup>
              <div class="form-check mt-2">
                <input
                  class="form-check-input"
                  id="check"
                  name="show_password"
                  v-model="showPasword"
                  type="checkbox"
                />
                <label class="form-check-label" for="check">Exibir senha</label>
              </div>
            </div>
          </div>
        </div>
        <div class="card-footer d-grid gap-2 p-3">
          <input
            class="btn btn-success btn-login fw-semibold"
            id="submit"
            name="submit"
            onclick="showLoad()"
            type="submit"
            value="Salvar Alterações"
          />
        </div>
      </form>
    </BOverlay>
  </div>
</template>
<style lang="css" scoped>
.slide-fade-enter-active {
  transition: all 0.4s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.4s cubic-bezier(1, 0.2, 0.4, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
