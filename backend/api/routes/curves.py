from fastapi import APIRouter, HTTPException

from api.curves import CURVE_REGISTRY
from api.models import CurveSummary, CurveDetail

router = APIRouter()


@router.get("/curves", response_model=list[CurveSummary])
async def list_curves():
    """Returns a list of available curves (id, name, description)."""
    return [
        CurveSummary(id=cid, name=c["name"], description=c["description"])
        for cid, c in CURVE_REGISTRY.items()
    ]


@router.get("/curves/{curve_id}", response_model=CurveDetail)
async def get_curve(curve_id: str):
    """Returns full parameters of a curve by ID."""
    curve = CURVE_REGISTRY.get(curve_id)
    if curve is None:
        raise HTTPException(status_code=404, detail=f"Curve '{curve_id}' not found")
    return CurveDetail(id=curve_id, **curve)
