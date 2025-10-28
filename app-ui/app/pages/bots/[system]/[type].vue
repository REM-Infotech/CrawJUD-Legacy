<script setup lang="ts">
import capa from "./_forms/capa.vue";
import protocolo from "./_forms/protocolo.vue";
const store = botStore();
const route = useRoute();
const { $router } = useNuxtApp();
const forms = {
  capa: capa,
  protocolo: protocolo,
};

function getComponent() {
  const comp = forms[route.params.type as "capa"];

  if (!comp) $router.push({ name: "bots" });

  return comp;
}

onMounted(() => {
  if (!store.bot) $router.push({ name: "bots" });
});
</script>

<template>
  <div>
    <BForm @submit="bots.startBot">
      <BContainer fluid="md">
        <AppCard class="form-card">
          <template #header>
            <span class="card-title">
              {{ store.bot?.display_name }}
            </span>
          </template>
          <template #body>
            <component :is="getComponent()" />
          </template>
          <template #footer>
            <div class="d-grid">
              <BButton type="submit" variant="outline-success"> Inicializar robô </BButton>
            </div>
          </template>
        </AppCard>
      </BContainer>
    </BForm>
  </div>
</template>

<style lang="css" scoped>
.form-card {
  min-height: 45em;
}
</style>
