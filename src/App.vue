<script setup lang="ts">
import { mainSocket } from "@/main";
import { useMessageStore } from "@/stores/message";
import { storeToRefs } from "pinia";
import { RouterView } from "vue-router";
import MainFrame from "./components/MainFrame.vue";
import router from "./router";

const { message } = storeToRefs(useMessageStore());
mainSocket.on("not_logged", () => {
  message.value = "Sessão expirada. Faça login novamente.";
  router.push({ name: "login" });
});
</script>

<template>
  <RouterView v-slot="{ Component }" class="hide-scroll">
    <MainFrame>
      <Transition name="fade" mode="out-in">
        <component :is="Component"></component>
      </Transition>
    </MainFrame>
  </RouterView>
</template>

<style lang="css" scoped>
.hide-scroll {
  scrollbar-width: none;
}
</style>
