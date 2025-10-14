<script setup lang="ts">
import { useBotFormStateInjected } from "@/composables/useBotFormState";

// Injeta apenas o estado do formulário que este componente precisa
const { form } = useBotFormStateInjected();
</script>
<template>
  <div class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <label class="form-label">Senha token</label>
    <input
      class="form-control"
      v-model="form.token"
      placeholder="Senha token"
      id="token"
      name="token"
      type="text"
      required
    />
  </div>
</template>
