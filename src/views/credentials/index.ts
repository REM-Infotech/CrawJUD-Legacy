import router from "@/router";

const credentials_routes = [
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
];

credentials_routes.forEach((route_) => router.addRoute(route_));
