<script setup lang="ts">
const {
  store: { botForm, opcoesCredenciais, progressBar, sidXlsxFile, sidUploadFiles },
} = bots.loadPlugins();

const selectedCredencial = ref<string>(null as unknown as string);
const arquivo_xlsx = ref<File>();
const outros_arquivos = ref<File[]>();

watch(selectedCredencial, (selectedOpt) => {
  botForm.value?.append("credencial_id", selectedOpt);
});

watch(arquivo_xlsx, async (arquivoXlsx) => {
  if (arquivoXlsx) {
    botForm.value?.append("xlsx", arquivoXlsx?.name as string);
    const uploader = new fileSheetUpload(arquivoXlsx as File);
    await uploader.upload();
  }
});

watch(outros_arquivos, async (outrosArquivos) => {
  const arquivos: string[] = [];
  if (outrosArquivos) {
    Array.from(outrosArquivos).forEach((file) => {
      arquivos.push(file.name);
    });

    botForm.value?.append("outros_arquivos", arquivos as unknown as string);
    const uploader = new multipleFileUpload(outrosArquivos);
    await uploader.upload();
  }
});

watch(sidXlsxFile, (newSid) => {
  if (newSid) {
    botForm.value?.append("xlsx_sid", newSid);
  }
});

watch(sidUploadFiles, (newSid) => {
  if (newSid) {
    botForm.value?.append("outros_arquivos_sid", newSid);
  }
});
</script>

<template>
  <div class="row g-2 p-3">
    <BCol md="12" lg="12" xl="12" sm="12">
      <BFormGroup label="Planilha Xlsx" label-size="lg">
        <BFormFile
          :disabled="progressBar > 0"
          v-model="arquivo_xlsx"
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
          v-model="outros_arquivos"
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
          v-model="selectedCredencial"
          :options="opcoesCredenciais"
          size="lg"
          class="mt-3"
        />
      </BFormGroup>
    </BCol>
  </div>
</template>
