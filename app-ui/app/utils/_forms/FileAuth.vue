<script setup lang="ts">
const {
  store: { botForm, opcoesCredenciais, progressBar },
} = bots.loadPlugins();

const selectedCredencial = ref<string>(null as unknown as string);
const arquivo_xlsx = ref<File>();

watch(selectedCredencial, (selectedOpt) => {
  console.log(selectedOpt);
  botForm.value?.append("credencial_id", selectedOpt);
});

watch(arquivo_xlsx, async (arquivoXlsx) => {
  console.log(arquivoXlsx);
  botForm.value?.append("xlsx", arquivoXlsx?.name as string);

  const uploader = new fileUpload(arquivoXlsx as File);
  await uploader.upload();
});
</script>

<template>
  <div class="row g-5 p-3">
    <BCol md="12" lg="12" xl="12" sm="12">
      <BFormGroup label="Planilha Xlsx" label-size="lg">
        <BFormFile
          v-model="arquivo_xlsx"
          class="mt-3"
          size="lg"
          accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
