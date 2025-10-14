<script setup lang="ts">
import formSetup from "@/views/botform/setup/formbot/scripts/formSetup";

const { form } = formSetup();
</script>

<template>
  <div class="col-md-12 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <BFormFile
      v-model="form.otherfiles as File"
      label="Arquivo Adicionais"
      label-class="form-label"
      class="form-control"
      placeholder="Arquivo Adicionais"
      id="xlsx"
      name="xlsx"
      type="file"
      :required="false"
      multiple
      :accept="['application/pdf']"
    />
  </div>
</template>
