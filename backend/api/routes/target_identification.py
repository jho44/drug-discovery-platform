from fastapi import APIRouter, HTTPException

from pipeline.target_identification.models import LitMiningRequest, LitMiningResult
from pipeline.target_identification.literature_mining import run_literature_mining

router = APIRouter(prefix="/target-identification", tags=["Target Identification"])


@router.post("/literature-mining", response_model=LitMiningResult)
async def literature_mining(request: LitMiningRequest):
    try:
        return await run_literature_mining(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
