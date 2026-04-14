from fastapi import APIRouter, HTTPException, Depends

from api.curves import CURVE_REGISTRY
from api.models import SolveRequest, SolveResponse, TaskResponse
from api.dependencies import get_task_manager
from api.services.task_manager import TaskManager
from ecdlp import solve_ecdlp
from fastecdsa.curve import Curve
from fastecdsa.point import Point

router = APIRouter()


def _build_solve_fn(P: Point, Q: Point, curve: Curve):
    """Returns a callable that runs solve_ecdlp and returns the scalar x."""
    def solve(cancel_event):
        return solve_ecdlp(P, Q, curve, cancel_token=cancel_event)
    return solve


@router.post("/solve", response_model=SolveResponse, status_code=202)
async def start_solve(
    req: SolveRequest,
    task_manager: TaskManager = Depends(get_task_manager),
):
    """
    Starts an ECDLP solve task.
    Server computes Q = x * P using the given curve, then runs the solver.
    Returns a task_id for polling status.
    """
    entry = CURVE_REGISTRY.get(req.curve_id)
    if entry is None:
        raise HTTPException(
            status_code=400,
            detail=f"Curve '{req.curve_id}' not found. Use GET /api/v1/curves to list available curves.",
        )

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
    Q = req.x * P

    task = task_manager.create_task()
    solve_fn = _build_solve_fn(P, Q, curve)
    task_manager.submit(task.task_id, req.curve_id, solve_fn)

    return SolveResponse(task_id=task.task_id, status=task.status)


@router.post("/tasks/{task_id}/cancel", response_model=TaskResponse)
async def cancel_solve(
    task_id: str,
    task_manager: TaskManager = Depends(get_task_manager),
):
    """Cancels a running solve task."""
    if not task_manager.cancel_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found or not cancellable")
    task = task_manager.get_task(task_id)
    return TaskResponse(
        task_id=task.task_id,
        status=task.status,
        curve_id=task.curve_id,
        result=task.result,
        error=task.error,
    )
