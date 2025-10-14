<script setup lang="ts">
import formSetup from "@/views/botform/setup/formbot/scripts/formSetup";

const { form } = formSetup();
</script>
<template>
  <div class="col-md-5 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <label class="form-label" for="doc_parte">CPF/CNPJ da parte</label>
    <input
      v-model="form.doc_parte"
      class="form-control"
      placeholder="CPF/CNPJ da parte"
      id="doc_parte"
      name="doc_parte"
      type="text"
    />
  </div>
</template>
