<script setup lang="ts">
import { onBeforeMount } from "vue";
import { useRouter } from "vue-router";
import { useModal } from "bootstrap-vue-next";
import { onMounted } from "vue";
import jQuery from "jquery";
import { loadingBuzy, onBuzyHidden, setBuzyClick } from "../../services/animations";
const router = useRouter();
import AuthService from "../../services/auth";

const { authenticate } = AuthService();

const $ = jQuery;

onMounted(() => {
  const { hide } = useModal("modal-load");
  const { show } = useModal("ModalMessage");
  hide();
  var message = sessionStorage.getItem("message");
  if (message) {
    $("#message").text(message);
    show();
    sessionStorage.removeItem("message");
  }
});

const handleSubmit = (e: Event) => {
  e.preventDefault();
  authenticate(router);
};

onBeforeMount(() => {
  if ($("#app").hasClass("bg-purple")) {
    $("#app").removeClass("bg-purple");
    $("#app").addClass("bg-indigo");
  }
});
</script>

<template>
  <main
    class="form-signin w-100 m-auto position-absolute top-50 start-50 translate-middle"
    data-bs-theme="light"
  >
    <img class="mb-4" src="@/assets/crawjud.png" alt="" width="80" height="80" />
    <h1 class="h3 mb-3 text-white fw-normal">CrawJUD v0.1.0</h1>
    <hr />
    <form method="post" @submit="handleSubmit">
      <div class="form-floating mb-3">
        <input type="text" name="" id="login" class="form-control" />
        <label for="login">Login</label>
      </div>
      <div class="form-floating mb-3">
        <input type="password" name="" id="password" class="form-control" />
        <label for="password">Password</label>
      </div>
      <hr />
      <BOverlay
        :show="loadingBuzy"
        rounded
        opacity="0.6"
        spinner-small
        spinner-variant="primary"
        class="d-inline-block"
        @hidden="onBuzyHidden"
      >
        <BButton
          type="button"
          ref="buzyButton"
          :disabled="loadingBuzy"
          variant="primary"
          @click="
            (e) => {
              setBuzyClick(e);
            }
          "
        >
          Login
        </BButton>
      </BOverlay>
    </form>
  </main>
</template>
