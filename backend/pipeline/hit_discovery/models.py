from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel

from pipeline.target_identification.models import CandidateTarget


class HitDiscoveryRequest(BaseModel):
    selected_targets: List[CandidateTarget]


class CompoundHit(BaseModel):
    compound_id: str
    name: Optional[str] = None
    smiles: Optional[str] = None
    molecular_weight: Optional[float] = None
    method: str                             # ligand_similarity | repurposing | fragment | hts
    source: str                             # ChEMBL | OpenTargets | PubChem
    activity_value: Optional[float] = None  # pChEMBL or assay value
    activity_unit: Optional[str] = None
    indication: Optional[str] = None        # repurposing: approved indication
    max_phase: Optional[int] = None         # clinical phase (repurposing)
    assay_id: Optional[str] = None
    consensus_score: Optional[float] = None
    image_url: Optional[str] = None


class TargetHits(BaseModel):
    target_name: str
    uniprot_id: Optional[str] = None
    chembl_target_id: Optional[str] = None
    ligand_based_hits: List[CompoundHit] = []
    repurposing_hits: List[CompoundHit] = []
    fragment_hits: List[CompoundHit] = []
    hts_hits: List[CompoundHit] = []
    consensus_hits: List[CompoundHit] = []
    claude_summary: str = ""
    methods_run: List[str] = []
    total_hits: int = 0


class HitDiscoveryResult(BaseModel):
    query_targets: List[str]
    target_results: List[TargetHits]
    overall_summary: str
    methods_used: List[str]
    total_compounds_found: int
