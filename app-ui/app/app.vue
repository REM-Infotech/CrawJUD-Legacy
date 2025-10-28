<script setup lang="ts">
import { BOrchestrator } from "bootstrap-vue-next";

const { $colormode } = useNuxtApp();

onBeforeMount(async () => {
  await $colormode.setup();
});
</script>
<template>
  <BToast />
  <BOrchestrator />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
<style>
.page-enter-active,
.page-leave-active {
  transition: all 0.4s;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
  filter: blur(1rem);
}
</style>
