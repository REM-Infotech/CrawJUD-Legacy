<script setup lang="ts">
import { onMounted, ref } from "vue";
import ProductService from "~/service/ProductService";

onMounted(() => {
  ProductService.getProductsMini().then((data) => (products.value = data));
});

const products = ref();
</script>
<template>
  <div></div>
</template>
