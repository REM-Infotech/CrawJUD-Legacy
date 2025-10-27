// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
import crawjud from "./theme/crawjud";

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  modules: ["@primevue/nuxt-module", "@pinia/nuxt"],
  primevue: {
    options: {
      ripple: true,
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
