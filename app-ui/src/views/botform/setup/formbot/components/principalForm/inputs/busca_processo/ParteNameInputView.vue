<script setup lang="ts">
import formSetup from "@/views/botform/setup/formbot/scripts/formSetup";

const { form } = formSetup();
</script>
<template>
  <div class="col-md-5 mb-3 border border-secondary p-2 border-2 rounded bg-body-tertiary">
    <label class="form-label">Nome da parte</label>
    <input
      class="form-control"
      v-model="form.parte_name"
      placeholder="Nome da parte"
      id="parte_name"
      name="parte_name"
      type="text"
      required
    />
  </div>
</template>
