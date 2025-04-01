<script setup lang="ts">
import { faFloppyDisk } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { useModal } from "bootstrap-vue-next";
import {
  current_action,
  form,
  submitForm,
  state_modal,
  submited,
  to_modal_message,
} from "../resources/formcred";

import { $, api } from "../../../main";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { computed, onBeforeMount, watch } from "vue";
import router from "../../route";
const { show: show_load, hide: hide_load } = useModal("modal-load");
const { show: show_message } = useModal("ModalMessage");
const { hide: hide_form } = useModal("ModalFormUsr");

// const state_email = computed(() => {
//   return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email);
// });
// const state_password = computed(() => {
//   return /^(?=.*[A-Za-z])(?=.*\d)(?=.*[\W_]).{6,}$/.test(form.password);
// });

watch(submited, (value) => {
  if (value) {
    show_load();
  }
});

watch(to_modal_message, (value) => {
  if (value) {
    hide_load();

    setTimeout(() => {
      show_message();
    }, 500);

    hide_form();

    to_modal_message.value = false;
  }
});

onBeforeMount(async () => {
  form.reset();

  api.get("/").catch((error) => {
    if (error.status === 401) {
      $("#message").text("É necessário fazer login para acessar esta página");
      router.push({ name: "Login" });

      setTimeout(() => {
        show_load();
      }, 500);
      show_message();
    } else {
      // console.error(error);;
    }
  });
});
</script>

<template>
  <BModal
    @hide="form.reset()"
    no-footer
    id="ModalFormUsr"
    data-bs-theme="dark"
    size="xl"
    centered
    class="text-white"
    :title="current_action"
  >
    <div>
      <BForm id="FormUsr" @submit="submitForm" v-model="state_modal" autocomplete="off">
        <BFormFloatingLabel class="mb-4" label-for="floatingName" label="Nome da Credencial">
          <BFormInput
            id="floatingName"
            v-model="form.name_credential"
            placeholder="Nome da Credencial"
            required
          />
        </BFormFloatingLabel>
        <!-- <BFormFloatingLabel class="mb-4" label-for="floatingEmail" label="E-mail">
          <BFormInvalidFeedback id="input-live-feedback"
            >Insira um email válido</BFormInvalidFeedback
          >
          <BFormInput
            v-model.trim="form.email"
            :state="state_email"
            id="floatingEmail"
            type="email"
            placeholder="E-mail"
            required
          />
        </BFormFloatingLabel> -->
        <BFormFloatingLabel class="mb-4" label-for="floatingLogin" label="Login">
          <BFormInput id="floatingLogin" v-model="form.login" placeholder="Login" required />
        </BFormFloatingLabel>
        <BFormFloatingLabel class="mb-4" label-for="floatingPassword" label="Senha:">
          <BFormInvalidFeedback id="floatingPassword-feedback"
            >Limite Minimo de 6 caracteres</BFormInvalidFeedback
          >
          <BFormInput
            autocomplete="off"
            type="password"
            id="floatingPassword"
            v-model.trim="form.password"
            placeholder="Senha"
            required
          />
        </BFormFloatingLabel>
        <hr />
        <div class="d-grid gap-2 mt-5 mb-2">
          <BButton type="submit" variant="outline-success">
            <span><FontAwesomeIcon class="me-2" :icon="faFloppyDisk" /></span>
            <em class="fw-bold">Salvar</em></BButton
          >
        </div>
      </BForm>
    </div>
  </BModal>
</template>
