<script setup lang="ts">
import NavBarComponent from "../../components/NavBarComponent.vue";
import SideBarComponent from "../../components/SideBarComponent.vue";
import BotForm from "./components/BotForm.vue";
import CardBot from "./components/CardBot.vue";
</script>

<template>
  <NavBarComponent />
  <div id="content" class="mt-4 mb-4">
    <SideBarComponent />
    <main>
      <BContainer fluid="lg" class="px-4">
        <CardBot />
      </BContainer>
    </main>
  </div>
  <BotForm />
</template>
