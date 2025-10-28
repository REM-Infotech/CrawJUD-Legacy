// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: ["@bootstrap-vue-next/nuxt", "@pinia/nuxt"],
  telemetry: false,
  bootstrapVueNext: {
    composables: true, // Will include all composables
    // composables: {useBreadcrumb: true, useColorMode: true, all: false}, // Will include only useBreadcrumb & useColorMode
    // composables: {useBreadcrumb: false, useColorMode: false, all: true} // Will include everything except useBreadcrumb & useColorMode
    directives: { all: true }, // Will include all directives
  },
  app: {
    pageTransition: { name: "page", mode: "out-in" },
  },
  css: ["bootstrap/dist/css/bootstrap.min.css", "~/assets/css/main.css"],
  plugins: [
    "~/plugins/bootstrap.client.ts",
    "~/plugins/datatables.client.ts",
    "~/plugins/colormode.ts",
  ],
  vite: {
    server: {
      allowedHosts: true,
    },
  },
});
