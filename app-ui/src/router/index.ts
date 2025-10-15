import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "login",
      component: () => import("@/views/auth/LoginView.vue"),
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: () => import("@/views/dashboard/DashboardView.vue"),
    },
    {
      path: "/logs/exec/:pid",
      name: "logs_execution",
      component: () => import("@/views/logsbot/LogsView.vue"),
    },
    {
      path: "/execucoes",
      name: "executions",
      redirect: {
        name: "dashboard",
      },
    },
    {
      path: "/tarefas_agendadas",
      name: "scheduled_tasks",
      redirect: {
        name: "dashboard",
      },
    },

    {
      path: "/bots",
      name: "bots",
      component: () => import("@/views/bots/BotsView.vue"),
    },
    {
      name: "bot_form",
      path: "/bot/:bot_id/:bot_system/:bot_type",
      component: () => import("@/views/bots/BotFormView.vue"),
    },
  ],
});

export default router;
