import axios from "axios";

axios.defaults.baseURL = new URL("", import.meta.env.VITE_API_URL).toString();

// Autenticação por cookies
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;
axios.defaults.xsrfCookieName = "X-Xsrf-Token";
axios.defaults.xsrfHeaderName = "X-Xsrf-Token";

export default defineNuxtPlugin((_) => {
  const api = axios.create({
    headers: {
      "Content-Type": "application/json, text/plain, */*",
    },
  });

  return {
    provide: {
      api,
    },
  };
});
