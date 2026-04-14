"""Socket.IO event handlers for the ECDLP solver.

Client → Server events:
    solve { curve_id, x }
    cancel { task_id }

Server → Client events (emitted by task_manager + handlers):
    task_started { task_id, curve_id }
    task_complete { task_id, status, result?, error? }
"""

from __future__ import annotations

from fastecdsa.curve import Curve
from fastecdsa.point import Point

from api.curves import CURVE_REGISTRY
from api.services.socket_manager import SocketManager
from api.services.task_manager import TaskManager
from ecdlp import solve_ecdlp


def _build_solve_fn(P: Point, Q: Point, curve: Curve):
    """Returns a callable that runs solve_ecdlp and returns the scalar x."""
    def solve(cancel_event):
        return solve_ecdlp(P, Q, curve, cancel_token=cancel_event)
    return solve


def register_handlers(socket_mgr: SocketManager, task_mgr: TaskManager) -> None:
    """Registers all socket.io event handlers on the AsyncServer."""
    sio = socket_mgr.sio

    @sio.on("solve")
    async def handle_solve(sid: str, data: dict):
        """Client requests a new solve: { curve_id, x }."""
        curve_id = data.get("curve_id")
        x = data.get("x")

        if not curve_id or x is None:
            await sio.emit(
                "task_complete",
                {"task_id": None, "status": "failed", "result": None,
                 "error": "Missing required fields: curve_id, x"},
                room=sid,
            )
            return

        entry = CURVE_REGISTRY.get(curve_id)
        if entry is None:
            await sio.emit(
                "task_complete",
                {"task_id": None, "status": "failed", "result": None,
                 "error": f"Curve '{curve_id}' not found"},
                room=sid,
            )
            return

        curve = Curve(
            name=entry["name"],
            p=entry["p"],
            a=entry["a"],
            b=entry["b"],
            q=entry["q"],
            gx=entry["gx"],
            gy=entry["gy"],
        )
        P = Point(entry["gx"], entry["gy"], curve=curve)
        Q = x * P

        task = task_mgr.create_task()
        solve_fn = _build_solve_fn(P, Q, curve)
        task_mgr.submit(task.task_id, curve_id, solve_fn, socket_manager=socket_mgr, sid=sid)

        await socket_mgr.emit_task_started(task.task_id, curve_id)

    @sio.on("cancel")
    async def handle_cancel(sid: str, data: dict):
        """Client requests cancellation: { task_id }."""
        task_id = data.get("task_id")
        if not task_id:
            await sio.emit(
                "task_complete",
                {"task_id": None, "status": "failed", "result": None,
                 "error": "Missing required field: task_id"},
                to=sid,
            )
            return

        if task_mgr.cancel_task(task_id):
            await sio.emit(
                "task_complete",
                {"task_id": task_id, "status": "cancelled", "result": None,
                 "error": None},
                to=sid,
            )
        else:
            await sio.emit(
                "task_complete",
                {"task_id": task_id, "status": "failed", "result": None,
                 "error": "Task not found or not cancellable"},
                to=sid,
            )
