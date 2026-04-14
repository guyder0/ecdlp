from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


# --- Curve schemas ---

class CurveSummary(BaseModel):
    id: str
    name: str
    description: str


class CurveDetail(BaseModel):
    id: str
    name: str
    description: str
    p: int
    a: int
    b: int
    gx: int
    gy: int
    q: int


# --- Solve schemas ---

class SolveRequest(BaseModel):
    curve_id: str = Field(..., description="ID of the curve to use")
    x: int = Field(..., gt=0, description="Secret scalar (server computes Q = x*P)")


class SolveResponse(BaseModel):
    task_id: str
    status: TaskStatus


# --- Task schemas ---

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    curve_id: Optional[str] = None
    result: Optional[int] = None
    error: Optional[str] = None
