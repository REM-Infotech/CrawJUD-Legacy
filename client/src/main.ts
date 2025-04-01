import "@popperjs/core";
import axios from "axios";
import { createBootstrap } from "bootstrap-vue-next";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.min.js";
import "datatables.net-select";
import jQuery from "jquery";
import "jquery/dist/jquery.min.js";
import { createApp } from "vue";
import "../plugins/axios.ts";
import App from "./App.vue";
import "./assets/main.css";
import "./assets/styles.css";
import router from "./routes/route.ts";

export const $ = jQuery;

function CreateApp() {
  const app = createApp(App);

  app.use(createBootstrap()); // Important
  app.use(router);

  app.mount("#app");
}
CreateApp();

const url_api = "https://api.reminfotech.net.br";

// Create axios instance with improved configuration
export const api = axios.create({
  baseURL: url_api,
  headers: {
    // Note: Changing the Content-Type may avoid the preflight but could affect your API expectations.
    "Content-Type": "application/x-www-form-urlencoded", // Use a "simple" header if possible
    "x-csrf-token": sessionStorage.getItem("x-csrf-token") || "",
  },
  withCredentials: true,
  withXSRFToken: true,
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);
