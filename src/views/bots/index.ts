import router from "@/router";

const bot_routes = [
  {
    path: "/bots",
    name: "bots",
    component: () => import("@/views/bots/BotsView.vue"),
  },
  {
    path: "/bot/:bot_id/:bot_system/:bot_type",
    name: "bot_form",
    component: () => import("@/views/botform/BotForm.vue"),
  },
];

bot_routes.forEach((route_) => router.addRoute(route_));
