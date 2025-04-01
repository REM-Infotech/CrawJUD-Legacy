<script setup lang="ts">
import TableConfig from "./Components/TableConfig.vue";
import NavBarComponent from "../../components/NavBarComponent.vue";
import SideBarComponent from "../../components/SideBarComponent.vue";
import ModalCadUsr from "./Components/UserForm.vue";
import { onBeforeMount } from "vue";
import { form } from "./resources/formusr";
import { $, api } from "../../main";
import { useModal } from "bootstrap-vue-next";
import { useRouter } from "vue-router";
const { show: show_load } = useModal("modal-load");
const { show: show_message } = useModal("ModalMessage");

const router = useRouter();

onBeforeMount(async () => {
  function toLogin() {
    $("#message").text("É necessário fazer login para acessar esta página");
    router.push({ name: "login" });

    setTimeout(() => {
      show_load();
    }, 500);
    show_message();
  }

  form.reset();

  api.get("/").catch((error) => {
    if (error.status === 401) {
      toLogin();
    } else if (error.code === "ERR_NETWORK") {
      toLogin();
    } else {
      // console.error(error);;
    }
  });
});
</script>

<template>
  <NavBarComponent />
  <div id="content" class="mt-4 mb-4">
    <SideBarComponent />
    <div>
      <main>
        <BContainer fluid="md" class="px-4">
          <h1 class="text-2xl font-bold mb-4 text-white">Configurações</h1>
          <TableConfig />
        </BContainer>
      </main>
      <ModalCadUsr />
    </div>
  </div>
</template>
