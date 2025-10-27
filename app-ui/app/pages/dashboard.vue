<script setup lang="ts">
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import { onMounted, ref } from "vue";
import ProductService from "~/service/ProductService";

onMounted(() => {
  ProductService.getProductsMini().then((data) => (products.value = data));
});

const products = ref();
</script>
<template>
  <div style="padding: 6.5rem">
    <Card style="height: 75%">
      <template #content>
        <DataTable :value="products" tableStyle="min-width: 50rem">
          <Column field="code" header="Code"></Column>
          <Column field="name" header="Name"></Column>
          <Column field="category" header="Category"></Column>
          <Column field="quantity" header="Quantity"></Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>
