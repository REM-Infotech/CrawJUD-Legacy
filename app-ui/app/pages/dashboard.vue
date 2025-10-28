<script setup lang="ts">
import DataTable from "datatables.net-vue3";
import AppCard from "~/components/AppCard.vue";

const bot = {
  id: "21",
  display_name: "JUSDS - Realizar Compromisso",
  system: "JUSDS",
  state: "EVERYONE",
  client: "INFRAERO",
  type: "REALIZA_PRAZO",
  form_cfg: "multipe_files",
  classification: "ADMINISTRATIVO",
  text: "Robô responsável por realizar compromissos no JUSDS",
};
const columns = [
  { data: "id", title: "#" },
  { data: "display_name", title: "Nome" },
  { data: "system", title: "Sistema" },
  { data: "text", title: "Descrição" },
];

const { $api } = useNuxtApp();
const botsResp = ref();

async function get_bot(_: unknown, callback: Function, __: unknown) {
  const resp = await $api.get("/bots/listagem");
  return callback(resp.data);
}
</script>
<template>
  <div>
    <AppCard>
      <template #body>
        <DataTable :columns="columns" :ajax="get_bot"> </DataTable>
      </template>
    </AppCard>
  </div>
</template>
