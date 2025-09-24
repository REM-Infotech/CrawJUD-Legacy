<script setup lang="ts">
import { useBotFormStateInjected } from "@/composables/useBotFormState";

// Injeta apenas o estado do formulário que este componente precisa
const { form } = useBotFormStateInjected();
</script>

<template>
  <div class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <div class="form-check form-switch">
      <input
        class="form-check-input"
        id="periodic_task"
        name="periodic_task"
        role="switch"
        type="checkbox"
        v-model="form.periodic_task"
      />
      <label class="form-check-label" for="periodic_task"
        >Execução periódica (experimental).
      </label>
    </div>
  </div>
</template>
