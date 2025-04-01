<script setup lang="ts">
import { ref } from "vue";
const modal = ref(false);
</script>

<template>
  <BModal
    data-bs-theme="light"
    v-model="modal"
    ok-only
    ok-title="Fechar"
    title="Mensagem"
    id="ModalMessage"
  >
    <p id="message"></p>
  </BModal>
</template>
