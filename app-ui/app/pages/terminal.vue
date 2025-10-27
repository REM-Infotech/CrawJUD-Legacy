<template>
  <AppHeader />
  <Toast />
  <NuxtLayout>
    <div style="min-width: 600px">
      <Terminal aria-label="PrimeVue Terminal Service" />
    </div>
    <Button label="Show" @click="show()" />
  </NuxtLayout>
</template>

<script setup lang="ts">
import TerminalService from "primevue/terminalservice";
import { onBeforeUnmount, onMounted } from "vue";

onMounted(() => {
  TerminalService.on("command", commandHandler);
});

onBeforeUnmount(() => {
  TerminalService.off("command", commandHandler);
});

const { $toast } = useNuxtApp();

function commandHandler(text: string) {
  let response: string | number;
  let argsIndex = text.indexOf(" ");
  let command = argsIndex !== -1 ? text.substring(0, argsIndex) : text;

  switch (command) {
    default:
      response = "Unknown command: " + command;
  }

  TerminalService.emit("response", response);
}
function show() {
  $toast.add({ severity: "info", summary: "Info", detail: "Message Content", life: 3000 });
}
</script>
