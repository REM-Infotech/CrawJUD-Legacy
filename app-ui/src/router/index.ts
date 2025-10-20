import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: {
        name: "logs",
      },
    },
    {
      path: "/logs",
      name: "logs",
      component: () => import("@/views/_logs/LogsView.vue"),
    },
  ],
});

export default router;
