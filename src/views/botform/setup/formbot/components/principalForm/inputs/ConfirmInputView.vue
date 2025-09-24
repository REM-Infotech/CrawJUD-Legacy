<script setup lang="ts">
import { useBotFormStateInjected } from "@/composables/useBotFormState";

// Injeta apenas o estado do formulário que este componente precisa
const { form } = useBotFormStateInjected();
</script>
<template>
  <div class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <div class="form-check">
      <input
        v-model="form.confirm_fields"
        class="form-check-input"
        id="confirm_fields"
        name="confirm_fields"
        required
        type="checkbox"
      />
      <label class="form-check-label"> Confirmo que os dados enviados estão corretos. </label>
    </div>
  </div>
</template>
