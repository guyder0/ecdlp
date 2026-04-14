from api.services.task_manager import TaskManager
from api.services.socket_manager import SocketManager

# Populated by main.py at startup
_task_manager: TaskManager | None = None
_socket_manager: SocketManager | None = None


def get_task_manager() -> TaskManager:
    """Returns the shared TaskManager instance."""
    if _task_manager is None:
        raise RuntimeError("TaskManager not initialized")
    return _task_manager


def set_task_manager(tm: TaskManager) -> None:
    global _task_manager
    _task_manager = tm


def get_socket_manager() -> SocketManager:
    """Returns the shared SocketManager instance."""
    if _socket_manager is None:
        raise RuntimeError("SocketManager not initialized")
    return _socket_manager


def set_socket_manager(sm: SocketManager) -> None:
    global _socket_manager
    _socket_manager = sm
