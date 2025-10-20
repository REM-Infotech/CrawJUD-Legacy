import "@/assets/js/color-modes.js";
import "@/assets/scss/main.css";
import "@/controllers/axios";
import "@/controllers/socketio";
import { manager } from "@/controllers/socketio";
import "@/views/bots";
import "@/views/config";
import "@/views/credentials";
import { createBootstrap } from "bootstrap-vue-next";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import "bootstrap/dist/css/bootstrap.css";
import DataTablesCore from "datatables.net-bs5";
import DataTable from "datatables.net-vue3";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

DataTable.use(DataTablesCore);
const app = createApp(App);
export const socketBots = manager.socket("/bots");
export const mainSocket = manager.socket("/master");
export const FileSocket = manager.socket("/files");
export const LogsBotSocket = manager.socket("/logsbot");
export const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(createBootstrap()); // Important
app.mount("#app");

router.afterEach((to) => {
  if (to.name !== "login") {
    setTimeout(() => {
      mainSocket.connect();
      socketBots.connect();
      FileSocket.connect();
    }, 1000);
  }
  if (to.name === "login") disconnectSocket();
});

/**
 * Disconnects all active socket connections used in the application.
 *
 * This function disconnects the following sockets:
 * - `mainSocket`: The primary socket connection.
 * - `socketBots`: The socket connection for bot-related communication.
 * - `FileSocket`: The socket connection for file operations.
 *
 * Use this function to gracefully close all socket connections, for example, when the user logs out or the application is shutting down.
 */
export function disconnectSocket() {
  mainSocket.disconnect();
  socketBots.disconnect();
  FileSocket.disconnect();
}
