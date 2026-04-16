from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import socketio
import os

from api.routes import health, curves, solve, tasks
from api.services.task_manager import TaskManager
from api.services.socket_manager import SocketManager
from api import dependencies
from api import socketio_handlers

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

sm = SocketManager()
dependencies.set_socket_manager(sm)

@asynccontextmanager
async def lifespan(app: FastAPI):
    tm = TaskManager(max_workers=4)
    dependencies.set_task_manager(tm)
    socketio_handlers.register_handlers(sm, tm)
    yield
    tm.shutdown()


app = FastAPI(
    title="ECDLP Solver API",
    description="REST API for solving Elliptic Curve Discrete Logarithm Problem",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router, prefix="", tags=["health"])
app.include_router(curves.router, prefix="/api/v1", tags=["curves"])
app.include_router(solve.router, prefix="/api/v1", tags=["solve"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

# Отдача фронта на продакшене
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return FileResponse(FRONTEND_DIST / "index.html")

app = socketio.ASGIApp(
    sm.sio, 
    other_asgi_app=app, 
    socketio_path="/ws"
)