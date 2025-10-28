interface Window {
  jQuery: typeof jQuery;
  $: typeof jQuery;
  axios: typeof Axios;
}

interface ImportMetaEnv {
  VITE_API_URL: string;
  VITE_BETA_TEST: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
