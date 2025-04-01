import { reactive, ref } from "vue";
import { $, api } from "../../../main";
export const form = reactive({
  id: 0,
  email: "",
  name: "",
  login: "",
  password: "",

  reset: () => {
    form.id = 0;
    form.email = "";
    form.name = "";
    form.login = "";
    form.password = "";
  },
});

export const delete_call = ref(false);
export const current_action = ref("");
export const state_modal = ref(false);

export const submited = ref(false);
export const to_modal_message = ref(false);

export async function submitForm(e: Event) {
  submited.value = true;

  e.preventDefault();

  const formData = new FormData();
  formData.append("nome_usuario", form.name);
  formData.append("login", form.login);
  formData.append("email", form.email);
  formData.append("password", form.password);

  if (current_action.value.includes("Editar")) {
    formData.append("id", form.id.toString());
    formData.append("method_request", "UPDATE");
  } else if (current_action.value.includes("Cadastrar")) {
    formData.append("method_request", "INSERT");
  } else if (delete_call.value === true) {
    formData.append("id", form.id.toString());
    formData.append("method_request", "DELETE");
  }

  api
    .post("/users", formData, {
      withXSRFToken: true,
      withCredentials: true,
      headers: {
        // Note: Changing the Content-Type may avoid the preflight but could affect your API expectations.
        "Content-Type": "application/x-www-form-urlencoded", // Use a "simple" header if possible
        "x-csrf-token": sessionStorage.getItem("x-csrf-token") || "",
      },
    })
    .then((response) => {
      if (response.status === 200) {
        $("#message").text(response.data.message);
      } else {
        $("#message").text(response.data.message);
      }
      to_modal_message.value = true;
    })

    .catch((response) => {
      console.log(response);

      $("#message").text(response.data.message);

      to_modal_message.value = true;
    });

  state_modal.value = false;
  submited.value = false;
}
