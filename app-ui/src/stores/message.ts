import { defineStore } from "pinia";
import { ref } from "vue";

const useMessageStore = defineStore("message", () => {
  const message = ref("");

  return { message };
});

export { useMessageStore };
