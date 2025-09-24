import { defineStore } from "pinia";
import { ref } from "vue";

export const useConfiguracoesStore = defineStore("ConfiguracoesStore", () => {
  const ConfiguracoesSelector = ref<ConfiguracoesSelectorRecord>({} as ConfiguracoesSelectorRecord);
  const UsersList = ref<UsersRecord[] | null>(null);

  return { ConfiguracoesSelector, UsersList };
});
