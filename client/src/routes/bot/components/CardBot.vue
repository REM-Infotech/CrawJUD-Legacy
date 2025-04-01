<script setup lang="ts">
import { onBeforeMount, ref } from "vue";
import { api } from "../../../main.ts";
import { useRouter } from "vue-router";
import { $ } from "../../../main.ts";
import { useModal } from "bootstrap-vue-next";
const router = useRouter();
const items = ref<{ system: string; id: number; display_name: string; text: string }[]>([]);
import { current_bot } from "../../../services/FormConfig.ts";

onBeforeMount(async () => {
  const { show: show_message } = useModal("ModalMessage");

  api
    .get("/bots_list")
    .then((resp) => {
      items.value = resp.data;
    })
    .catch((response) => {
      // check if response.status is 4** error
      if (response.response.status === 401 || response.response.status === 422) {
        $("#message").text("É necessário estar autenticado para acessar essa página.");
        router.push({ name: "login" });
        show_message();
      }
    });
});
</script>

<template>
  <div class="row">
    <div class="col-md-3 p-4 end-0" v-for="item in items" :key="item.id">
      <BCard v-if="item.system.toLowerCase() === 'projudi'" data-bs-theme="dark" tag="article">
        <template #header>
          <span class="fw-bold">{{ item.display_name }}</span>
        </template>
        <template #img>
          <img src="@/assets/projudi.png" alt="" />
        </template>
        <BCardBody style="height: 6rem" class="overflow-y-auto">
          <span class="overflow-auto" style="height: 50rem">{{ item.text }} </span>
        </BCardBody>
        <template #footer>
          <div class="dropdown">
            <BButton
              class="btn me-2 fw-bold dropdown-toggle"
              variant="outline-success"
              @click="current_bot = item"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <em>Acessar Robô</em>
            </BButton>
            <ul class="dropdown-menu mt-2">
              <li>
                <a class="dropdown-item" href="#" v-b-modal.ModalFormBot>
                  <em>Execução normal</em>
                </a>
              </li>
              <li>
                <a class="dropdown-item" href="#">
                  <em>Execução agendada</em>
                </a>
              </li>
            </ul>
          </div>
        </template>
      </BCard>
      <BCard v-else data-bs-theme="dark" tag="article">
        <template #header>
          <span class="fw-bold">{{ item.display_name }}</span>
        </template>
        <BCardBody style="height: 6rem" class="overflow-y-auto">
          <span style="height: 50rem">{{ item.text }} </span>
        </BCardBody>
        <template #img>
          <img src="@/assets/crawjud2.svg" alt="" />
        </template>
        <template #footer>
          <div class="dropdown">
            <BButton
              class="btn me-2 fw-bold dropdown-toggle"
              variant="outline-success"
              @click="current_bot = item"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <em>Acessar Robô</em>
            </BButton>
            <ul class="dropdown-menu mt-2">
              <li>
                <a class="dropdown-item" href="#" v-b-modal.ModalFormBot>
                  <em>Execução normal</em>
                </a>
              </li>
              <li>
                <a class="dropdown-item" href="#">
                  <em>Execução agendada</em>
                </a>
              </li>
            </ul>
          </div>
        </template>
      </BCard>
    </div>
  </div>
</template>
