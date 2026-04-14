"""Socket.IO manager — wraps the socketio.AsyncServer for task events."""

import socketio


class SocketManager:
    """Thin wrapper around socketio.AsyncServer with typed emit helpers."""

    def __init__(self) -> None:
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

    # -- event emitters (server → client) --------------------------------

    async def emit_task_started(self, task_id: str, curve_id: str) -> None:
        await self.sio.emit(
            "task_started", {"task_id": task_id, "curve_id": curve_id},
        )

    async def emit_task_complete(
        self, task_id: str, status: str, result: int | None = None, error: str | None = None
    ) -> None:
        await self.sio.emit(
            "task_complete",
            {"task_id": task_id, "status": status, "result": result, "error": error},
        )

    async def emit_task_error(self, task_id: str, error: str) -> None:
        await self.sio.emit(
            "task_complete",
            {"task_id": task_id, "status": "failed", "result": None, "error": error},
        )
