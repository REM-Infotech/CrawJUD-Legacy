/// <reference types="vite/client" />

interface ImportMetaEnv {
  VITE_API_URL: string;
  VITE_BETA_TEST: string;
  VITE_MINIO_ENDPOINT: string;
  VITE_MINIO_ACCESS_KEY: string;
  VITE_MINIO_SECRET_KEY: string;
  VITE_MINIO_BUCKET_NAME: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
