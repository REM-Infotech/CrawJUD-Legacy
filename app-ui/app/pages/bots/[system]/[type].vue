<script setup lang="ts">
import capa from "./_forms/capa.vue";

const route = useRoute();
const { $router } = useNuxtApp();
const forms = {
  capa: capa,
};

function getComponent() {
  const comp = forms[route.params.type as "capa"];

  if (!comp) $router.push({ name: "bots" });

  return comp;
}
</script>

<template>
  <div>
    <component :is="getComponent()" />
  </div>
</template>
