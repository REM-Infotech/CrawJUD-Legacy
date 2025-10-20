<script setup lang="ts">
import { BApp } from "bootstrap-vue-next";
import { RouterView } from "vue-router";
import FooterView from "./components/footer/FooterView.vue";
import HeaderView from "./components/header/HeaderView.vue";
</script>

<template>
  <BApp>
    <div class="content">
      <HeaderView />
      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
      <FooterView />
    </div>
  </BApp>
</template>

<style lang="css">
.content {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
