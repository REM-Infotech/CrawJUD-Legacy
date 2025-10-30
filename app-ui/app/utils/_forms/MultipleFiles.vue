<script setup lang="ts">
const { progressBar, opcoesCredenciais } = storeToRefs(botStore());

const MultipleFilesForm = reactive<RecordMultipleFilesForm>({
  ArquivoXlsx: undefined,
  Credential: null,
  OutrosArquivos: undefined,
});

watch(() => MultipleFilesForm.ArquivoXlsx, FormManager.uploadXlsx);
watch(() => MultipleFilesForm.OutrosArquivos, FormManager.uploadMultipleFiles);
watch(() => MultipleFilesForm.Credential, FormManager.LoadCredential);
</script>

<template>
  <div class="row g-2 p-3">
    <BCol md="12" lg="12" xl="12" sm="12">
      <BFormGroup label="Planilha Xlsx" label-size="lg">
        <BFormFile
          :disabled="progressBar > 0"
          v-model="MultipleFilesForm.ArquivoXlsx"
          class="mt-3"
          size="lg"
          accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        />
      </BFormGroup>
    </BCol>
    <BCol md="12" lg="12" xl="12" sm="12">
      <BFormGroup label="Anexos" label-size="lg">
        <BFormFile
          :disabled="progressBar > 0"
          multiple
          v-model="MultipleFilesForm.OutrosArquivos"
          class="mt-3"
          size="lg"
          accept="application/pdf"
        />
      </BFormGroup>
    </BCol>
    <BCol md="12" lg="12" xl="12" sm="12">
      <Transition name="page" mode="in-out">
        <div v-if="progressBar > 0" class="d-grid">
          <BProgress :value="progressBar" :max="100" />
        </div>
      </Transition>
    </BCol>
    <BCol md="12" lg="12" xl="12" sm="12">
      <BFormGroup label="Credencial" label-size="lg">
        <BFormSelect
          v-model="MultipleFilesForm.Credential"
          :options="opcoesCredenciais"
          size="lg"
          class="mt-3"
        />
      </BFormGroup>
    </BCol>
  </div>
</template>
