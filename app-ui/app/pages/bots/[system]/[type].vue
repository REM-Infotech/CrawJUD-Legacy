<script setup lang="ts">
import { useHead } from "#app";
import { storeToRefs } from "pinia";
const { $router } = useNuxtApp();

const { bot, btnConfirm, confirmedState, progressBar } = storeToRefs(botStore());

onBeforeMount(FormManager.RetrieveCredentials);

useHead({
  title: bot.value?.display_name,
});
</script>

<template>
  <div>
    <BForm @submit="(ev: Event) => FormManager.HandleSubmit(ev)">
      <BContainer fluid="md">
        <AppCard class="form-card">
          <template #header>
            <span class="card-title fs-3">
              {{ bot?.display_name }}
            </span>
          </template>
          <template #body>
            <component :is="FormManager.getForm()" />
            <div class="box">
              <BFormCheckbox
                id="checkbox-1"
                name="checkbox-1"
                value="accepted"
                :unchecked-value="false"
                v-model="btnConfirm"
                class="mt-3 mb-4"
              >
                <span class="fs-6 fw-bold"> Confirmo que os dados enviados estão corretos. </span>
              </BFormCheckbox>
            </div>
          </template>
          <template #footer>
            <div class="d-grid gap-2" style="height: 6.5em">
              <div class="box d-grid">
                <Transition name="startbot" mode="out-in">
                  <BButton
                    size="md"
                    v-if="confirmedState && progressBar === 0"
                    type="submit"
                    variant="outline-success"
                  >
                    <span class="fs-6 fw-bold"> Inicializar robô </span>
                  </BButton>
                </Transition>
              </div>
              <div class="box d-grid">
                <BButton size="md" variant="outline-primary">
                  <span class="fs-6 fw-bold"> Gerar planilha Modelo </span>
                </BButton>
              </div>
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

.box {
  height: 2.5em;
}
</style>
