<script setup lang="ts">
import { DataTable } from "datatables.net-vue3";
import { onMounted, ref } from "vue";
import AppCard from "~/components/AppCard.vue";
import ProductService from "~/service/ProductService";

onMounted(() => {
  ProductService.getProductsMini().then((data) => (products.value = data));
});

const products = ref();
</script>
<template>
  <div>
    <AppCard>
      <template #body>
        <DataTable> </DataTable>
      </template>
    </AppCard>
  </div>
</template>
