import { Manager } from "socket.io-client";
const uri = new URL("", import.meta.env.VITE_API_URL).toString();
export default new Manager(uri, {
  withCredentials: true,
  extraHeaders: {
    "Content-Type": "application/json",
  },
});
