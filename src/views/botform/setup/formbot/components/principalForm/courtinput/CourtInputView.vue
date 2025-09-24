<script setup lang="ts">
import formSetup from "@/views/botform/setup/formbot/scripts/formSetup";
import { BFormGroup, BFormSelect, BInput } from "bootstrap-vue-next";

const { form, queryCourt, queryCourtOptionsCourt } = formSetup();
</script>

<template>
  <div class="col-md-10 mb-3 border border-secondary p-2 border-2 rounded" data-select2-id="22">
    <label class="form-label">Selecione a Vara</label>
    <BFormGroup
      class="mb-4"
      id="fieldset-filter-court"
      floating
      label="Filtre Aqui"
      description="Filtre por aqui as varas desejadas"
    >
      <BInput placeholder="Filtro de varas" id="input-filter-court" trim v-model="queryCourt" />
    </BFormGroup>
    <BFormSelect
      v-model="form.varas"
      :options="queryCourtOptionsCourt"
      :select-size="7"
      :multiple="true"
      required
    />
  </div>
</template>
