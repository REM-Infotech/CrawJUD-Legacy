<script setup lang="ts">
import formSetup from "@/views/botform/setup/formbot/scripts/formSetup";

const { form, stateOptions } = formSetup();
</script>

<template>
  <div class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <label class="form-label">Selecione o Estado</label>
    <BFormSelect v-model="form.state" :options="stateOptions" />
  </div>
</template>
