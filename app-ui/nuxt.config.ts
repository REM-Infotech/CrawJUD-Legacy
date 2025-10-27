// https://nuxt.com/docs/api/configuration/nuxt-config
import crawjud from "./theme/crawjud";

import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  modules: ["@primevue/nuxt-module"],
  primevue: {
    options: {
      theme: {
        preset: crawjud,
      },
    },
  },
  css: ["~/assets/css/main.css"],
  devtools: { enabled: true },
  vite: {
    plugins: [tailwindcss()],
    build: {
      sourcemap: true,
    },
  },
  app: {
    pageTransition: { name: "page", mode: "out-in" },
  },
});
