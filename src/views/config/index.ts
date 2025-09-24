import router from "@/router";
import type { RouteRecordRaw } from "vue-router";

const config_routes: RouteRecordRaw[] = [
  {
    path: "/configuracoes",
    name: "configuracoes",
    component: () => import("@/views/config/ConfiguracoesView.vue"),
  },
  {
    path: "/usuario/:metodo",
    name: "newUser",
    component: () => import("@/views/config/form/UserConfigFormView.vue"),
  },
];

config_routes.forEach((route_) => router.addRoute(route_));
