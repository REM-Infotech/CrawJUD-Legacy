import "@/assets/js/color-modes.js";
import "@/assets/scss/main.scss";
import "@/res/axios";
import "@/res/socketio";

import { createBootstrap } from "bootstrap-vue-next";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import "bootstrap/dist/css/bootstrap.css";

import DataTablesCore from "datatables.net-bs5";
import DataTable from "datatables.net-vue3";

import { createPinia } from "pinia";
import { createApp } from "vue";

// Main App
import App from "./App.vue";
import router from "./router";

// Configure DataTables
DataTable.use(DataTablesCore);

const app = createApp(App);
export const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(createBootstrap()); // Important
app.mount("#app");
