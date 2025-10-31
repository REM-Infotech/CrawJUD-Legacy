import axios, { isAxiosError } from "axios";

const url = new URL("", import.meta.env.VITE_API_URL).toString();

const api = axios.create({
  baseURL: url,
  headers: {
    "Content-Type": "application/json, text/plain, */*",
  },
  withCredentials: true,
  xsrfCookieName: "x-xsrf-token",
  xsrfHeaderName: "x-xsrf-token",
  withXSRFToken: true,
});

// Add a 401 response interceptor
api.interceptors.response.use(
  function (response) {
    return response;
  },
  async function (error) {
    if (isAxiosError(error)) {
      const { $toast: toast, $router: router } = useNuxtApp();
      if (error.response) {
        if (error.response.status && 401 === error.response.status) {
          toast.create({
            title: "Erro",
            body: error.response.data.message,
            variant: "danger",
            noCloseButton: true,
            noAnimation: true,
            noProgress: true,
            modelValue: 5000,
          });

          await api.post("/auth/logout");
          router.push({ name: "login" });
          return;
        }
      } else if (error.code === "ERR_NETWORK") {
        toast.create({
          title: "Erro do servidor",
          body: "Servidor fora do ar, tente novamente mais tarde",
          variant: "danger",
          noCloseButton: true,
          noAnimation: true,
          noProgress: true,
          modelValue: 5000,
        });
        router.push({ name: "login" });
        return;
      } else {
        return Promise.reject(error);
      }
    } else {
      return Promise.reject(error);
    }
  },
);

export default api;
