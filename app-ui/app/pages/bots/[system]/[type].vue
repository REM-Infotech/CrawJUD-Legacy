<script setup lang="ts">
import { useHead } from "#app";
const { $router } = useNuxtApp();
const {
  store: { bot, botForm, btnConfirm, confirmedState, progressBar },
} = bots.loadPlugins();

onMounted(() => {
  if (!bot.value) $router.push({ name: "bots" });
  botForm.value = new FormData();
});

onBeforeMount(async () => {
  await bots.loadCredentials();
});

onUnmounted(() => {
  botForm.value = undefined;
});

useHead({
  title: bot.value?.display_name,
});

function handleSubmit(ev: Event) {
  ev.preventDefault();

  bots.startBot(botForm.value as FormData);
}
</script>

<template>
  <div>
    <BForm @submit="handleSubmit">
      <BContainer fluid="md">
        <AppCard class="form-card">
          <template #header>
            <span class="card-title fs-3">
              {{ bot?.display_name }}
            </span>
          </template>
          <template #body>
            <component :is="bots.getComponent()" />
          </template>
          <template #footer>
            <div class="d-grid gap-3">
              <BFormCheckbox
                id="checkbox-1"
                name="checkbox-1"
                value="accepted"
                :unchecked-value="false"
                v-model="btnConfirm"
                class="mt-3 mb-4 fs-4"
              >
                Confirmo que os dados enviados estão corretos.
              </BFormCheckbox>
              <Transition name="startbot" mode="out-in">
                <BButton
                  size="lg"
                  v-if="confirmedState && progressBar === 0"
                  type="submit"
                  variant="outline-success"
                >
                  Inicializar robô
                </BButton>
              </Transition>
              <BButton size="lg" variant="outline-primary"> Gerar planilha Modelo </BButton>
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

.startbot-enter-active,
.startbot-leave-active {
  transition: all 0.4s;
}
.startbot-enter-from,
.startbot-leave-to {
  opacity: 0;
  filter: blur(1rem);
}
</style>
