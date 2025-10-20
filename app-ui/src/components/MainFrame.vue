<script setup lang="ts">
import styled from "@vue-styled-components/core";
import { computed } from "vue";
import { useRoute } from "vue-router";
import ModalMessage from "./ModalMessage.vue";
import NavbarView from "./NavbarView.vue";
import OffcanvasView from "./OffcanvasView.vue";

const route = useRoute();

const StyledFrame = styled.div`
  position: fixed;
  overflow-y: auto;
  height: 100%;
  width: 100%;
  top: 56px;
  max-height: calc(100dvh - 56px);
  margin-bottom: 70px;
  scrollbar-width: none;
`;

const computedClassStyledFrame = computed(() => {
  return route.name === "login" ? "d-flex" : "d-grid mt-auto mb-auto";
});

const loginPage = computed(() => {
  return route.name === "login" ? true : false;
});
</script>

<template>
  <Transition name="fade" mode="out-in">
    <NavbarView v-if="!loginPage" />
  </Transition>
  <OffcanvasView />
  <StyledFrame :class="computedClassStyledFrame">
    <div class="container-fluid mt-3 mb-3 d-flex">
      <slot></slot>
    </div>
  </StyledFrame>

  <ModalMessage />
</template>

<style lang="css"></style>
