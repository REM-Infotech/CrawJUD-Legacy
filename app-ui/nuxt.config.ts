// https://nuxt.com/docs/api/configuration/nuxt-config
import Aura from "@primeuix/themes/aura";

import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  modules: ["@primevue/nuxt-module", "@pinia/nuxt"],
  primevue: {
    options: {
      theme: {
        preset: Aura,
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