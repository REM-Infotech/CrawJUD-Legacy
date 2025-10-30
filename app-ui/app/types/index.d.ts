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

type MessageType = "success" | "info" | "error" | "warning";

interface Element {
  focus(): void;
}

type NotificationDirection = "auto" | "ltr" | "rtl";
interface NotificationOptions {
  badge?: string;
  body?: string;
  data?: any;
  dir?: NotificationDirection;
  icon?: string;
  lang?: string;
  requireInteraction?: boolean;
  silent?: boolean | null;
  tag?: string;
}
type KeywordArgs = {
  title: string;
  message: string;
  type: MessageType;
  duration: number;
};
