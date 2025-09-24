<script setup lang="ts">
import logoCrawJUD from "@/assets/img/crawjud2.png";
import { api } from "@/controllers/axios";
import { useMessageStore } from "@/stores/message";

import { isAxiosError } from "axios";
import { storeToRefs } from "pinia";
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
const router = useRouter();
const showOverlay = ref(false);
const Form = reactive({
  login: "",
  password: "",
  remember_me: false,
});

async function handleSubmit(e: Event) {
  e.preventDefault();
  showOverlay.value = true;
  let message = "Erro ao realizar login";
  let isLogged = false;
  try {
    const form = new FormData();

    Object.entries(Form).map(([key, value]) => form.append(key, value));

    const response = await api.request({ method: "POST", data: form, url: "/login" });
    const data = response.data;

    message = data.message;
    isLogged = true;
  } catch (err) {
    if (isAxiosError(err) && err.response && err.response.data && err.response.data.message) {
      const data = err.response.data;
      message = data.message;
    }
  }
  const { message: msg } = storeToRefs(useMessageStore());
  msg.value = message;
  if (isLogged) {
    router.push({ name: "dashboard" });
  }
  showOverlay.value = false;
}

document.title = "CrawJUD";
</script>

<template>
  <main class="form-signin w-100 m-auto mt-auto">
    <BOverlay :show="showOverlay" rounded="sm" opacity="0.2" class="p-5">
      <form @submit="handleSubmit">
        <img class="mb-4" :src="logoCrawJUD" alt="Logo CrawJUD" width="75" />
        <h1 class="h3 mb-3 fw-normal">CrawJUD</h1>
        <div class="form-floating">
          <input
            type="text"
            class="form-control"
            id="floatingInput"
            placeholder="You Login"
            v-model="Form.login"
          />
          <label for="floatingInput">Login</label>
        </div>
        <div class="form-floating">
          <input
            type="password"
            class="form-control"
            id="floatingPassword"
            placeholder="Password"
            v-model="Form.password"
          />
          <label for="floatingPassword">Password</label>
        </div>
        <div class="form-check text-start my-3">
          <input
            class="form-check-input"
            type="checkbox"
            :value="false"
            id="checkDefault"
            v-model="Form.remember_me"
          />
          <label class="form-check-label" for="checkDefault"> Salvar Sessão </label>
        </div>
        <button class="btn btn-primary w-100 py-2" type="submit">Sign in</button>
        <p class="mt-5 mb-3 text-body-secondary">CrawJUD &copy; 2022–2025</p>
      </form>
    </BOverlay>
  </main>
</template>
