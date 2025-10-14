<script setup lang="ts">
import { socketBots } from "@/res";
import { api } from "@/res/axios";
import { useCredentialsStore } from "@/stores/credentials";
import { useMessageStore } from "@/stores/message";
import { isAxiosError } from "axios";
import { storeToRefs } from "pinia";
import { reactive } from "vue";
import { useRouter } from "vue-router";

const { credentialsSelector } = storeToRefs(useCredentialsStore());
const { message } = storeToRefs(useMessageStore());
const router = useRouter();
const Form = reactive({
  auth_method: null,
  nome_cred: null,
  system: null,
  login: null,
  password: null,
  cert: null,
  doc_cert: null,
  key: null,
});

socketBots.emit("bot_credentials", (credentialsData: CredentialsSelectorRecord) => {
  credentialsSelector.value = credentialsData;
});

async function handleSubmit(e: Event) {
  e.preventDefault();

  if (!Form.system) {
    message.value = "É necessário informar ao menos um sistema!";
    return;
  }

  if (!Form.auth_method) {
    message.value = "Informe o método de login!";
    return;
  }

  let msg = "Erro ao salvar credencial";
  let success = false;
  try {
    const resp = await api.post("/peform_credencial", Form);

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
    router.push({ name: "credentials" });
  }
}
</script>

<template>
  <div class="container px-4">
    <form
      class="card border-0 shadow rounded-3 my-5"
      @submit="handleSubmit"
      name="CadastroProcesso"
      enctype="multipart/form-data"
    >
      <h4 class="card-header p-4">Credenciais - Cadastro</h4>
      <div class="card-body p-4 p-sm-5">
        <div class="row g-3 rounded justify-content-center p-3">
          <div class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded">
            <label class="form-label" for="nome_cred">Nome da credencial</label>
            <input
              class="form-control"
              id="nome_cred"
              name="nome_cred"
              placeholder="Nome da credencial"
              required
              type="text"
              v-model="Form.nome_cred"
            />
          </div>
          <div class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded">
            <label class="form-label" for="system">Selecione o sistema</label>
            <select
              required
              class="form-control select2-hidden-accessible"
              id="system"
              name="system"
              placeholder="Selecione o sistema"
              data-select2-id="system"
              tabindex="-1"
              aria-hidden="true"
              v-model="Form.system"
            >
              <option :value="null">Selecione</option>
              <option value="PROJUDI">PROJUDI</option>
              <option value="ESAJ">ESAJ</option>
              <option value="ELAW">ELAW</option>
              <option value="CAIXA">CAIXA</option>
              <option value="TJDFT">TJDFT</option>
              <option value="PJE">PJE</option>
              <option value="CSI">CSI</option>
              <option value="JUSDS">JUSDS</option>
            </select>
          </div>
          <div class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded">
            <label class="form-label" for="auth_method">Selecione o método de login</label>
            <select
              class="form-control select2-hidden-accessible"
              id="auth_method"
              name="auth_method"
              v-model="Form.auth_method"
              placeholder="Selecione o método de login"
              data-select2-id="auth_method"
              tabindex="-1"
              aria-hidden="true"
            >
              <option :value="null">Selecione</option>
              <option value="cert">Certificado</option>
              <option value="pw">Login/Senha</option>
            </select>
          </div>
          <Transition name="slide-fade" mode="out-in">
            <div id="pw" class="col-md-10" v-if="Form.auth_method === 'pw'">
              <div class="row">
                <div class="col-md-6 mb-3 border border-secondary p-2 border-2 rounded">
                  <label class="form-label" for="login">Usuário</label>
                  <input
                    class="form-control"
                    id="login"
                    name="login"
                    placeholder="Usuário"
                    type="text"
                    v-model="Form.login"
                    :required="Form.auth_method === 'pw'"
                  />
                </div>
                <div class="col-md-6 mb-3 border border-secondary p-2 border-2 rounded">
                  <label class="form-label" for="password">Senha</label>
                  <input
                    class="form-control"
                    id="password"
                    name="password"
                    placeholder="Senha"
                    type="password"
                    v-model="Form.password"
                    :required="Form.auth_method === 'pw'"
                  />
                </div>
              </div>
            </div>
            <div id="cert" class="col-md-10" v-else-if="Form.auth_method === 'cert'">
              <div class="row">
                <div class="col-md-12 mb-4 border border-secondary p-2 border-2 rounded">
                  <label class="form-label" for="doc_cert">CPF/CNPJ do Certificado</label>
                  <input
                    class="form-control"
                    id="doc_cert"
                    name="doc_cert"
                    placeholder="CPF/CNPJ do Certificado"
                    type="text"
                    v-model="Form.doc_cert"
                    :required="Form.auth_method === 'cert'"
                  />
                </div>
                <div class="col-md-6 mb-3 border border-secondary p-2 border-2 rounded">
                  <BFormFile
                    id="cert"
                    name="cert"
                    class="form-control"
                    label-class="form-label"
                    v-model="Form.cert"
                    :required="Form.auth_method === 'cert'"
                    label="Selecione o certificado"
                    accept=".pfx"
                  />
                </div>
                <div class="col-md-6 mb-3 border border-secondary p-2 border-2 rounded">
                  <label class="form-label" for="key">Informe a senha do certificado</label>
                  <input
                    class="form-control"
                    id="key"
                    name="key"
                    placeholder="Informe a senha do certificado"
                    type="text"
                    v-model="Form.key"
                    :required="Form.auth_method === 'cert'"
                  />
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
      <div class="card-footer d-grid p-3">
        <button
          class="btn btn-success btn-login fw-semibold"
          id="submit"
          name="submit"
          type="submit"
        >
          <span> Salvar </span>
        </button>
      </div>
    </form>
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
