import { Manager } from "socket.io-client";
export default defineNuxtPlugin((_) => {
  const uri = new URL("", import.meta.env.VITE_API_URL).toString();
  const socketio = new Manager(uri, {
    withCredentials: true,
    extraHeaders: {
      "Content-Type": "application/json",
    },
  });

  return {
    provide: {
      socketio,
    },
  };
});
