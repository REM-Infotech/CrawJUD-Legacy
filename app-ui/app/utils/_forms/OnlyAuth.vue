<script setup lang="ts">
import { storeToRefs } from "pinia";

const { opcoesCredenciais, botForm } = storeToRefs(botStore());

const OnlyAuthForm = reactive<RecordOnlyAuthForm>({
  Credencial: null,
});

watch(OnlyAuthForm, (newValue) => (botForm.value = newValue));
</script>

<template>
  <div class="row g-2 p-3">
    <BCol md="12" lg="12" xl="12" sm="12">
      <BFormGroup label="Credencial" label-size="lg">
        <BFormSelect
          v-model="OnlyAuthForm.Credencial"
          :options="opcoesCredenciais"
          size="lg"
          class="mt-3"
        />
      </BFormGroup>
    </BCol>
  </div>
</template>
