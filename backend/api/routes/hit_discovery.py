from fastapi import APIRouter, HTTPException

from pipeline.hit_discovery.models import HitDiscoveryRequest, HitDiscoveryResult
from pipeline.hit_discovery.hit_identification import run_hit_identification

router = APIRouter(prefix="/hit-discovery", tags=["Hit Discovery"])


@router.post("/run", response_model=HitDiscoveryResult)
async def run_hit_discovery(request: HitDiscoveryRequest):
    try:
        return await run_hit_identification(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
