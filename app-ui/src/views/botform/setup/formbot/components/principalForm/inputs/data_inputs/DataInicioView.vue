<script setup lang="ts">
import formSetup from "@/views/botform/setup/formbot/scripts/formSetup";

const { form } = formSetup();
</script>

<template>
  <div class="col-md-5 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <label class="form-label" for="data_inicio">Data de Início</label>
    <input
      v-model="form.data_inicio"
      class="form-control"
      placeholder="Data de Início"
      id="data_inicio"
      name="data_inicio"
      type="date"
    />
  </div>
</template>
