<script setup lang="ts">
import formSetup from "@/views/botform/setup/formbot/scripts/formSetup";

const { form } = formSetup();
</script>

<template>
  <div class="col-md-12 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <BFormFile
      v-model="form.xlsx as File"
      label="Arquivo de execução"
      label-class="form-label"
      class="form-control"
      placeholder="Arquivo de execução"
      id="xlsx"
      name="xlsx"
      type="file"
      required
      accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    />
  </div>
</template>
