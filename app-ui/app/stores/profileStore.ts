import { defineStore } from "pinia";

export default defineStore("profile", () => {
  const menu = ref();
  const toggle = (event: unknown) => {
    menu.value.toggle(event);
  };

  return { toggle, menu };
});
