<template>
  <BModal v-model="modal" ok-only title="Mensagem"> {{ message }} </BModal>
</template>

<script setup lang="ts">
import { api } from "@/controllers/axios";
import { useMessageStore } from "@/stores/message";

import { storeToRefs } from "pinia";
import { ref, watch } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const { message } = storeToRefs(useMessageStore());
const modal = ref(false);

watch(message, () => {
  if (message.value !== "") {
    modal.value = true;
  }
});

watch(modal, (newValue) => {
  if (!newValue) {
    message.value = "";
  }
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      modal.value = true;
      message.value = "Sessão expirada. Faça login novamente.";
      router.push({ name: "login" });
    }
    return Promise.reject(error);
  },
);
</script>
