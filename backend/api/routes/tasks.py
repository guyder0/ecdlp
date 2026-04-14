from fastapi import APIRouter, HTTPException, Depends

from api.models import TaskResponse
from api.dependencies import get_task_manager

router = APIRouter()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    task_manager = Depends(get_task_manager),
):
    """Returns the current status of a solve task."""
    task = task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(
        task_id=task.task_id,
        status=task.status,
        curve_id=task.curve_id,
        result=task.result,
        error=task.error,
    )
