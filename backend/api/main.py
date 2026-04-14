from contextlib import asynccontextmanager
from fastapi import FastAPI
import socketio

from api.routes import health, curves, solve, tasks
from api.services.task_manager import TaskManager
from api.services.socket_manager import SocketManager
from api import dependencies
from api import socketio_handlers

tm = TaskManager(max_workers=4)
sm = SocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    dependencies.set_task_manager(tm)
    dependencies.set_socket_manager(sm)
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

app = socketio.ASGIApp(
    sm.sio, 
    other_asgi_app=app, 
    socketio_path="/ws"
)