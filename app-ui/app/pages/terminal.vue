<script setup lang="ts">
import TerminalService from "primevue/terminalservice";
import { onBeforeUnmount, onMounted } from "vue";

onMounted(() => {
  TerminalService.on("command", commandHandler);
});

onBeforeUnmount(() => {
  TerminalService.off("command", commandHandler);
});

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
</script>

<template>
  <div>
    <div style="min-width: 600px">
      <Terminal class="bg-black" aria-label="PrimeVue Terminal Service" />
    </div>
  </div>
</template>

<style>
.p-terminal {
  background-color: black;
}
</style>
