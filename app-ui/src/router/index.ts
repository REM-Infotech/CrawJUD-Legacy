import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "login",
      component: () => import("@/views/LoginView.vue"),
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
      path: "/credentials",
      name: "credentials",
      component: () => import("@/views/credentials/CredentialsView.vue"),
    },
    {
      path: "/credentials/new",
      name: "newCredential",
      component: () => import("@/views/credentials/form/CredentialsFormView.vue"),
    },
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
  ],
});

export default router;
