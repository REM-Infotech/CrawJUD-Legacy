<script setup lang="ts">
import NavBarComponent from "../../components/NavBarComponent.vue";
import SideBarComponent from "../../components/SideBarComponent.vue";
import ChartComponent from "./components/ChartComponent.vue";
import TableComponent from "../../components/TableComponent.vue";
import { useModal } from "bootstrap-vue-next";
import jQuery from "jquery";
import { onMounted } from "vue";

const $ = jQuery;

onMounted(() => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { show, hide, modal } = useModal("ModalMessage");
  var message = sessionStorage.getItem("message");
  if (message) {
    $("#message").text(message);
    show();
    sessionStorage.removeItem("message");
  }
});
</script>

<template>
  <NavBarComponent />
  <div id="content" class="mt-4 mb-4">
    <SideBarComponent />
    <div>
      <main>
        <BContainer fluid class="px-4">
          <ChartComponent />
          <TableComponent />
        </BContainer>
      </main>
    </div>
  </div>
</template>
