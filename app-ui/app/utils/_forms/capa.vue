<script setup lang="ts">
const { bot, opcoesCredenciais } = botStore();

const selected = ref(null);
</script>

<template>
  <div class="row g-5 p-3">
    <BCol md="12" lg="12" xl="12" sm="12">
      <BFormGroup label="Planilha Xlsx" label-size="lg">
        <BFormFile
          class="mt-3"
          size="lg"
          accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        />
      </BFormGroup>
    </BCol>
    <BCol md="12" lg="12" xl="12" sm="12">
      <BFormGroup label="Credencial" label-size="lg">
        <BFormSelect v-model="selected" :options="opcoesCredenciais" size="lg" class="mt-3" />
      </BFormGroup>
    </BCol>
  </div>
</template>
