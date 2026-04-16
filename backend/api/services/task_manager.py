import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from typing import Dict, Optional

from api.models import TaskStatus
from ecdlp.exceptions import CalculationInterrupted


@dataclass
class Task:
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    curve_id: Optional[str] = None
    result: Optional[int] = None
    error: Optional[str] = None
    cancel_event: threading.Event = field(default_factory=threading.Event)
    future: Optional[Future] = None


class TaskManager:
    """Manages solve tasks with thread pool execution and cancellation support."""

    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: Dict[str, Task] = {}

    def shutdown(self) -> None:
        """Shuts down the thread pool, cancelling all running tasks."""
        for task in self._tasks.values():
            if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                task.cancel_event.set()
        self._executor.shutdown(wait=False)

    def create_task(self) -> Task:
        """Creates a new pending task and returns it."""
        task_id = str(uuid.uuid4())
        task = Task(task_id=task_id)
        self._tasks[task_id] = task
        return task

    def submit(
        self,
        task_id: str,
        curve_id: str,
        fn,
        socket_manager=None,
        sid: str | None = None,
    ) -> Task:
        """Submits a solve function to the thread pool and starts execution."""
        task = self._tasks[task_id]
        task.curve_id = curve_id
        task.status = TaskStatus.RUNNING
        task.future = self._executor.submit(fn, task.cancel_event)
        task.future.add_done_callback(self._on_complete(task_id, socket_manager, sid))
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Signals cancellation for a running task."""
        task = self._tasks.get(task_id)
        if task is None:
            return False
        if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
            task.cancel_event.set()
            return True
        return False

    def _on_complete(self, task_id: str, socket_manager=None, sid: str | None = None):
        """Returns a callback that updates task status on completion."""
        import asyncio
        loop = asyncio.get_event_loop()

        def callback(future: Future):
            task = self._tasks.get(task_id)
            if task is None:
                return
            try:
                task.result = future.result()
                task.status = TaskStatus.COMPLETED
            except CalculationInterrupted:
                task.status = TaskStatus.CANCELLED
            except Exception as exc:
                task.status = TaskStatus.FAILED
                task.error = str(exc)

            if socket_manager and sid:
                loop.create_task(
                    socket_manager.emit_task_complete(
                        task_id,
                        task.status.value,
                        result=task.result,
                        error=task.error,
                    )
                )
        return callback
