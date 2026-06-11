from pydantic import BaseModel

# Inputs accepted from target_identification stage
from pipeline.target_identification.models import CandidateTarget


class HitDiscoveryRequest(BaseModel):
    selected_targets: list[CandidateTarget]


class HitCompound(BaseModel):
    compound_id: str
    name: str
    smiles: str
    target: str
    docking_score: float | None = None
    similarity_score: float | None = None


class HitDiscoveryResult(BaseModel):
    hits: list[HitCompound]
