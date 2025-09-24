import { defineStore } from "pinia";
import { ref } from "vue";

export const useCredentialsStore = defineStore("credentialsStore", () => {
  const credentialsSelector = ref<CredentialsSelectorRecord>({} as CredentialsSelectorRecord);
  const credentialsList = ref<CredentialsRecord[] | null>(null);

  return { credentialsSelector, credentialsList };
});
