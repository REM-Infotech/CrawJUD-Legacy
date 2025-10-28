interface Window {
  jQuery: typeof jQuery;
  $: typeof jQuery;
  axios: typeof AxiosInstance;
  matchMedia: typeof window.matchMedia;
}

interface ImportMetaEnv {
  VITE_API_URL: string;
  VITE_BETA_TEST: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Element {
  focus(): void;
}
