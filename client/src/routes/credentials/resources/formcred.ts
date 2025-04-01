import { AxiosError, AxiosResponse } from "axios";
import { reactive, ref } from "vue";
import { $, api } from "../../../main";
export const form = reactive({
  id: 0,
  name_credential: "",
  login: "",
  password: "",

  reset: () => {
    form.id = 0;
    form.name_credential = "";
    form.login = "";
    form.password = "";
  },
});

export const selected2 = ref(null);
export const systems_list = ref<unknown[]>([{ value: null, text: "Carregando", disabled: true }]);

export const delete_call = ref(false);
export const current_action = ref("");
export const state_modal = ref(false);

export const submited = ref(false);
export const to_modal_message = ref(false);

export async function submitForm(e: Event) {
  submited.value = true;
  e.preventDefault();

  const systembot = selected2.value as unknown as string;
  const formData = new FormData();
  formData.append("nome_cred", form.name_credential);
  formData.append("system", systembot);
  formData.append("auth_method", "pw");
  formData.append("login", form.login);
  formData.append("password", form.password);

  api
    .post("/peform_credencial", formData, {
      withXSRFToken: true,
      withCredentials: true,
      headers: {
        // Note: Changing the Content-Type may avoid the preflight but could affect your API expectations.
        "Content-Type": "application/x-www-form-urlencoded", // Use a "simple" header if possible
        "x-csrf-token": sessionStorage.getItem("x-csrf-token") || "",
      },
    })
    .then((response: AxiosResponse) => {
      if (response.status === 200) {
        $("#message").text(response.data.message);
      }
      to_modal_message.value = true;
    })
    .catch((error: AxiosError) => {
      const response = error.response as AxiosResponse;
      const message = response.data.message as string;

      $("#message").text(message);

      to_modal_message.value = true;
    });

  state_modal.value = false;
  submited.value = false;
}
