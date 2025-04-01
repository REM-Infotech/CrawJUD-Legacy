import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import { BootstrapVueNextResolver } from "bootstrap-vue-next";
import Components from "unplugin-vue-components/vite";
import { defineConfig } from "vite";
import vueDevTools from "vite-plugin-vue-devtools";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    Components({
      resolvers: [BootstrapVueNextResolver()],
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./client/src", import.meta.url)),
    },
  },
  server: {
    allowedHosts: ["195.200.1.226", "crawjud2.robotz.dev", "crawjud.reminfotech.net.br"],
    port: 8000,
    strictPort: true,
    host: true,
    origin: "https://crawjud.reminfotech.net.br",

    // proxy: {
    //   "/acquire_credentials": {
    //     target: "http://195.200.1.226:5000",
    //     // changeOrigin: true,
    //   },
    //   "/auth": {
    //     target: "http://195.200.1.226:5000",
    //     // changeOrigin: true,
    //     secure: false,
    //   },
    //   "/logout": {
    //     target: "http://195.200.1.226:5000",
    //     // changeOrigin: true,
    //   },
    //   "/executions": {
    //     target: "http://195.200.1.226:5000",
    //     // changeOrigin: true,
    //   },
    //   "/bots_list": {
    //     target: "http://195.200.1.226:5000",
    //     // changeOrigin: true,
    //   },
    // },
  },
});
