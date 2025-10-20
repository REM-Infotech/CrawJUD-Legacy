import "@/assets/js/color-modes";
import "@/assets/scss/main.css";

import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import "bootstrap/dist/css/bootstrap.css";

import { createBootstrap } from "bootstrap-vue-next";
import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";

import DataTablesCore from "datatables.net-bs5";
import DataTable from "datatables.net-vue3";

DataTable.use(DataTablesCore);
const app = createApp(App);
export const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(createBootstrap()); // Important
app.mount("#app");
