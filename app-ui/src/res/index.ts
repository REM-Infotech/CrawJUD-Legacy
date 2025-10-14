import { manager } from "@/res/socketio";

const socketBots = manager.socket("/bots");
const mainSocket = manager.socket("/master");
const FileSocket = manager.socket("/files");
const LogsBotSocket = manager.socket("/logsbot");

export { FileSocket, LogsBotSocket, mainSocket, socketBots };
