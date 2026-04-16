import { io, Socket } from "socket.io-client";

export interface TaskStartedData {
  task_id: string;
  curve_id: string;
}

export interface TaskCompleteData {
  task_id: string | null;
  status: "success" | "failed" | "cancelled";
  result?: string;
  error?: string;
}

// Интерфейсы для событий (Type safety)
interface ServerToClientEvents {
  task_started: (data: TaskStartedData) => void;
  task_complete: (data: TaskCompleteData) => void;
}

interface ClientToServerEvents {
  solve: (data: { curve_id: string; x: string }) => void;
  cancel: (data: { task_id: string }) => void;
}

export const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io({
  path: "/ws",
  transports: ["websocket"],
  autoConnect: true,
});

socket.on("connect", () => {
  console.log("Connected to WebSocket, SID:", socket.id);
});

socket.on("disconnect", () => {
  console.log("Disconnected from WebSocket");
});

export default socket;