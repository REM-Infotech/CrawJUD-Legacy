<script setup lang="ts">
import { useBotFormRefsInjected, useBotFormStateInjected } from "@/composables/useBotFormState";
import { socketBots } from "@/res";
import { onBeforeMount } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// Injeta o estado e referências necessárias
const { form, bot, credentialsSelector, message } = useBotFormStateInjected();
const { selectCredentialsRef } = useBotFormRefsInjected();

onBeforeMount(() => {
  if (!credentialsSelector.value) {
    socketBots.emit("bot_credentials_select", (credentialsData: CredentialsSelectorRecord) => {
      credentialsSelector.value = credentialsData;
    });
  }
  if (!bot.value) {
    router.push({ name: "bots" });
    return;
  }

  setTimeout(() => {
    const creds = credentialsSelector.value;
    if (creds && bot.value) {
      selectCredentialsRef.value = creds[bot.value?.system.toLowerCase()];
      if ((selectCredentialsRef.value as unknown[]).length === 1) {
        message.value = "É necessário cadastrar uma credencial!";
        router.push({ name: "bots" });
      }
    }
  }, 750);
});
</script>

<template>
  <div class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <label class="form-label">Selecione a Credencial</label>
    <BFormSelect v-model="form.creds" :options="selectCredentialsRef" />
  </div>
</template>
