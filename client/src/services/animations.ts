import { ref } from "vue";

let timeout: ReturnType<typeof setTimeout> | null = null;

export const loadingBuzy = ref(false);
export const buzyButton = ref<HTMLElement | null>(null);

const clearTimer = () => {
  if (timeout) {
    clearTimeout(timeout);
    timeout = null;
  }
};

const setTimer = (callback) => {
  clearTimer();
  timeout = setTimeout(() => {
    clearTimer();
    callback();
  }, 2500);
};

export const setBuzyClick = (e: Event) => {
  const form = (e.currentTarget as HTMLElement).closest("form");
  if (form) {
    form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
  }

  loadingBuzy.value = true;
  // Simulate an async request
  setTimer(() => {
    loadingBuzy.value = false;
  });
};

export const onBuzyHidden = () => {
  // Return focus to the button once hidden
  //buzyButton.focus()
};
