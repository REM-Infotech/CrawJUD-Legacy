import axios from "axios";

const url = new URL("", import.meta.env.VITE_API_URL).toString();

const api = axios.create({
  baseURL: url,
  headers: {
    "Content-Type": "application/json, text/plain, */*",
  },
  withCredentials: true,
  xsrfCookieName: "X-Xsrf-Token",
  xsrfHeaderName: "X-Xsrf-Token",
  withXSRFToken: true,
});

// Add a 401 response interceptor
api.interceptors.response.use(
  function (response) {
    return response;
  },
  function (error) {
    if (401 === error.response.status) {
      const { $toast: toast, $router: router } = useNuxtApp();

      toast.create({
        title: "Sessão expirada!",
        body: "Sua sessão foi expirada.",
        variant: "warning",
        noCloseButton: true,
        noAnimation: true,
        noProgress: true,
        modelValue: 1500,
      });

      router.push({ name: "login" });
    } else {
      return Promise.reject(error);
    }
  },
);

export default api;
