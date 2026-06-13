from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class LitMiningRequest(BaseModel):
    query: str = Field(..., description="Free-text PubMed search query")
    max_abstracts: int = Field(default=15, ge=1, le=40)


class Evidence(BaseModel):
    pmid: str
    quote: str
    relation: str


class CandidateTarget(BaseModel):
    name: str
    type: str
    rationale: str
    confidence: str
    evidence: list[Evidence]


class Relation(BaseModel):
    subject: str
    relation: str
    object: str
    pmid: str


class Entities(BaseModel):
    genes_proteins: list[str]
    diseases: list[str]


class AbstractMeta(BaseModel):
    pmid: str
    title: str
    authors: list[str]
    journal: str
    year: str


class LitMiningResult(BaseModel):
    query: str
    abstracts_fetched: int
    abstracts_meta: list[AbstractMeta]
    entities: Entities
    relations: list[Relation]
    candidate_targets: list[CandidateTarget]
    summary: str


# --- Enrichment models (OpenTargets + Human Protein Atlas) ---

class EnrichmentRequest(BaseModel):
    original_query: str
    candidate_targets: list[CandidateTarget]


class GeneticAssociationEvidence(BaseModel):
    disease_name: str
    association_score: float
    source: str = "OpenTargets"


class TractabilityEvidence(BaseModel):
    small_molecule_score: Optional[float]
    antibody_score: Optional[float]
    assessment: str


class OpenTargetsEvidence(BaseModel):
    ensembl_id: Optional[str]
    tractability: Optional[TractabilityEvidence]
    genetic_associations: list[GeneticAssociationEvidence]
    mouse_phenotypes: list[str]
    safety_liabilities: list[str]


class TissueExpressionEvidence(BaseModel):
    tissue: str
    rna_level: str  # "High" | "Medium" | "Low" | "Not detected"


class CancerPathologyEvidence(BaseModel):
    cancer_type: str
    high_expression_percent: float
    survival_correlation: Optional[str]


class HPAEvidence(BaseModel):
    protein_class: list[str]
    tissue_expression: list[TissueExpressionEvidence]
    cancer_pathology: list[CancerPathologyEvidence]
    subcellular_locations: list[str]
    hpa_url: Optional[str]


class EnrichedTarget(BaseModel):
    literature: CandidateTarget
    opentargets: Optional[OpenTargetsEvidence]
    hpa: Optional[HPAEvidence]
    integrated_confidence: str  # "high" | "medium" | "low"
    integrated_rationale: str
    validation_summary: str
    consensus_score: Optional[float]
    methods_confirmed: int
    total_methods: int = 3


class EnrichmentResult(BaseModel):
    original_query: str
    enriched_targets: list[EnrichedTarget]
    enrichment_summary: str
    methods_used: list[str]
    targets_enriched: int
    targets_not_found_in_ot: list[str]
    targets_not_found_in_hpa: list[str]
