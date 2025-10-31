<script setup lang="ts">
import { storeToRefs } from "pinia";

const { progressBar, opcoesCredenciais } = storeToRefs(botStore());

const MultipleFilesForm = reactive<RecordMultipleFilesForm>({
  ArquivoXlsx: undefined,
  Credential: null,
  OutrosArquivos: undefined,
});

const XlsxFileUpload = ref(false);
const OutrosArquivosUpload = ref(false);

watch(
  () => MultipleFilesForm.ArquivoXlsx,
  async (newVal) => {
    XlsxFileUpload.value = true;
    await FormManager.uploadXlsx(newVal);
    XlsxFileUpload.value = false;
  },
);
watch(
  () => MultipleFilesForm.OutrosArquivos,
  async (newVal) => {
    OutrosArquivosUpload.value = true;
    await FormManager.uploadMultipleFiles(newVal);
    OutrosArquivosUpload.value = false;
  },
);
watch(
  () => MultipleFilesForm.Credential,
  async (newVal) => FormManager.LoadCredential(newVal),
);
</script>

<template>
  <div class="row g-2 p-3">
    <BCol md="12" lg="12" xl="12" sm="12">
      <div class="container-fluid rounded rounded-4 border p-3" style="height: 8.5rem">
        <BFormGroup label="Planilha Xlsx" class="mb-2" label-size="lg">
          <BFormFile
            :disabled="progressBar > 0"
            v-model="MultipleFilesForm.ArquivoXlsx"
            class="mt-3"
            size="lg"
            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          />
        </BFormGroup>
        <Transition name="page" mode="in-out">
          <div v-if="progressBar > 0 && XlsxFileUpload" class="d-grid">
            <BProgress :value="progressBar" :max="100" />
          </div>
        </Transition>
      </div>
    </BCol>
    <BCol md="12" lg="12" xl="12" sm="12">
      <div class="container-fluid rounded rounded-4 border p-3" style="height: 8.5rem">
        <BFormGroup label="Anexos" class="mb-2" label-size="lg">
          <BFormFile
            :disabled="progressBar > 0"
            multiple
            v-model="MultipleFilesForm.OutrosArquivos"
            class="mt-3"
            size="lg"
            accept="application/pdf"
          />
        </BFormGroup>
        <Transition name="page" mode="in-out">
          <div v-if="progressBar > 0 && OutrosArquivosUpload" class="d-grid">
            <BProgress :value="progressBar" :max="100" />
          </div>
        </Transition>
      </div>
    </BCol>
    <BCol md="12" lg="12" xl="12" sm="12"> </BCol>
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
