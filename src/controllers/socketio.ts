import { Manager } from "socket.io-client";

const uri = new URL("", import.meta.env.VITE_API_URL).toString();
export const manager = new Manager(uri, {
  withCredentials: true,
  autoConnect: true,
  extraHeaders: {
    "Content-Type": "application/json",
  },
});
