<script setup lang="ts">
const { progressBar, opcoesCredenciais } = storeToRefs(botStore());

const FormFileAuth = reactive<RecordFileAuthForm>({
  ArquivoXlsx: undefined,
  Credential: null,
});

watch(() => FormFileAuth.ArquivoXlsx, FormManager.uploadXlsx);
watch(() => FormFileAuth.Credential, FormManager.LoadCredential);
</script>

<template>
  <div class="row g-2 p-3">
    <BCol md="12" lg="12" xl="12" sm="12" class="container rounded rounded-4">
      <BFormGroup label="Planilha Xlsx" label-size="lg">
        <BFormFile
          v-model="FormFileAuth.ArquivoXlsx"
          class="mt-3"
          size="lg"
          accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          required
        />
      </BFormGroup>
      <Transition name="page" mode="in-out">
        <div v-if="progressBar > 0" class="d-grid">
          <BProgress :value="progressBar" :max="100" />
        </div>
      </Transition>
    </BCol>
    <BCol md="12" lg="12" xl="12" sm="12"> </BCol>
    <BCol md="12" lg="12" xl="12" sm="12">
      <BFormGroup label="Credencial" label-size="lg">
        <BFormSelect
          v-model="FormFileAuth.Credential"
          :options="opcoesCredenciais"
          size="lg"
          class="mt-3"
          required
        />
      </BFormGroup>
    </BCol>
  </div>
</template>
