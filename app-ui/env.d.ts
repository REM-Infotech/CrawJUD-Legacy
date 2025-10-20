/// <reference types="vite/client" />
import "./src/types";
interface ImportMetaEnv {
  VITE_API_URL: string;
  VITE_BETA_TEST: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module "*.js" {}
