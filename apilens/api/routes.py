from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics")
def get_metrics():
    # TODO: Return aggregated metrics from DB
    return {"status": "ok", "metrics": {}}
