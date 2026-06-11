from fastapi import APIRouter

from api.routes import target_identification, hit_discovery, lead_optimization, preclinical, clinical_trials, regulatory_approval

router = APIRouter()

router.include_router(target_identification.router)
router.include_router(hit_discovery.router)
router.include_router(lead_optimization.router)
router.include_router(preclinical.router)
router.include_router(clinical_trials.router)
router.include_router(regulatory_approval.router)
