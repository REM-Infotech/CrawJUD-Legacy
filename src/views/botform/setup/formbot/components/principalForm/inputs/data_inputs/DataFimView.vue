<script setup lang="ts">
import formSetup from "@/views/botform/setup/formbot/scripts/formSetup";

const { form } = formSetup();
</script>

<template>
  <div class="col-md-5 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <label class="form-label" for="data_fim">Data Fim</label>
    <input
      v-model="form.data_fim"
      class="form-control"
      placeholder="Data Fim"
      id="data_fim"
      name="data_fim"
      type="date"
    />
  </div>
</template>
