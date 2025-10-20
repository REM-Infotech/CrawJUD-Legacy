import { Manager } from "socket.io-client";

const uri = new URL(import.meta.env.VITE_API_URL).toString();

const socketio = new Manager(uri, {
  autoConnect: false,
});

export default socketio;
