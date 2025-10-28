import axios from "axios";

axios.defaults.baseURL = new URL("", import.meta.env.VITE_API_URL).toString();

export default defineNuxtPlugin((_) => {
  const api = axios.create({
    headers: {
      "Content-Type": "application/json, text/plain, */*",
    },
    withCredentials: true,
    xsrfCookieName: "X-Xsrf-Token",
    xsrfHeaderName: "X-Xsrf-Token",
    withXSRFToken: true,
  });

  return {
    provide: {
      api,
    },
  };
});
