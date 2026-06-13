"""Target enrichment pipeline: OpenTargets + HPA + Claude integrated synthesis."""

from __future__ import annotations
import asyncio
import re

from config.settings import settings
from services.opentargets_client import get_opentargets_data, OpenTargetsResult
from services.human_protein_atlas_client import get_hpa_data, HPAResult
from services.claude_client import synthesize_enriched_targets
from services.ensemble import compute_consensus
from pipeline.target_identification.models import (
    EnrichmentRequest,
    EnrichmentResult,
    EnrichedTarget,
    OpenTargetsEvidence,
    HPAEvidence,
    GeneticAssociationEvidence,
    TractabilityEvidence,
    TissueExpressionEvidence,
    CancerPathologyEvidence,
)


def _normalize(name: str) -> str:
    return re.sub(r"[\s\-]?[A-Z]\d+[A-Z]?$", "", name.strip().upper())


def _ot_to_model(result: OpenTargetsResult) -> OpenTargetsEvidence:
    tract = result.tractability
    tract_model = TractabilityEvidence(
        small_molecule_score=tract.small_molecule,
        antibody_score=tract.antibody,
        assessment=_tractability_assessment(tract.small_molecule, tract.antibody),
    ) if tract else None

    return OpenTargetsEvidence(
        ensembl_id=result.ensembl_id,
        tractability=tract_model,
        genetic_associations=[
            GeneticAssociationEvidence(
                disease_name=a.disease_name,
                association_score=a.score,
            )
            for a in result.top_genetic_associations
        ],
        mouse_phenotypes=result.mouse_phenotypes,
        safety_liabilities=result.safety_liabilities,
    )


def _tractability_assessment(sm: float | None, ab: float | None) -> str:
    score = sm or ab or 0.0
    if score >= 0.7:
        modality = "small molecule" if (sm or 0) >= (ab or 0) else "antibody"
        return f"High confidence {modality} tractable"
    if score >= 0.3:
        return "Moderate tractability"
    return "Low tractability or insufficient data"


def _hpa_to_model(result: HPAResult) -> HPAEvidence:
    return HPAEvidence(
        protein_class=result.protein_class,
        tissue_expression=[
            TissueExpressionEvidence(tissue=t.tissue, rna_level=t.rna_level)
            for t in result.tissue_expression
        ],
        cancer_pathology=[
            CancerPathologyEvidence(
                cancer_type=c.cancer_type,
                high_expression_percent=c.high_expression_percent,
                survival_correlation=c.survival_correlation,
            )
            for c in result.cancer_pathology
        ],
        subcellular_locations=result.subcellular_locations,
        hpa_url=result.hpa_url,
    )


def _build_bundle(name: str, candidate: dict, ot: OpenTargetsEvidence | None, hpa: HPAEvidence | None) -> dict:
    return {
        "name": name,
        "literature": candidate,
        "opentargets": ot.model_dump() if ot else None,
        "hpa": hpa.model_dump() if hpa else None,
    }


async def run_target_enrichment(request: EnrichmentRequest) -> EnrichmentResult:
    # Cap to max_targets_to_enrich (candidates already ordered by lit mining confidence)
    candidates = request.candidate_targets[: settings.max_targets_to_enrich]
    names = [c.name for c in candidates]
    symbols = [_normalize(n) for n in names]

    # Fan out OT + HPA in parallel
    ot_results, hpa_results = await asyncio.gather(
        get_opentargets_data(symbols),
        get_hpa_data(symbols),
    )

    # Convert raw dataclasses to Pydantic models; track missing
    ot_models: list[OpenTargetsEvidence | None] = []
    hpa_models: list[HPAEvidence | None] = []
    not_found_ot: list[str] = []
    not_found_hpa: list[str] = []

    for name, ot_raw, hpa_raw in zip(names, ot_results, hpa_results):
        if ot_raw is not None:
            ot_models.append(_ot_to_model(ot_raw))
        else:
            ot_models.append(None)
            not_found_ot.append(name)

        if hpa_raw is not None:
            hpa_models.append(_hpa_to_model(hpa_raw))
        else:
            hpa_models.append(None)
            not_found_hpa.append(name)

    # Build evidence bundles for Claude
    bundles = [
        _build_bundle(name, c.model_dump(), ot, hpa)
        for name, c, ot, hpa in zip(names, candidates, ot_models, hpa_models)
    ]

    # Claude synthesis
    synthesis = await synthesize_enriched_targets(request.original_query, bundles)

    # Build a lookup for Claude synthesis results
    synthesis_by_name = {
        e["name"].strip().upper(): e
        for e in synthesis.get("enriched_targets", [])
    }

    # Ensemble scoring across 3 methods
    lit_cands = [{"name": n} for n in names]
    ot_cands = [{"name": n} for n, r in zip(names, ot_results) if r is not None]
    hpa_cands = [{"name": n} for n, r in zip(names, hpa_results) if r is not None]
    scored = compute_consensus([lit_cands, ot_cands, hpa_cands])
    score_by_name = {s.name: s for s in scored}

    # Assemble final enriched targets
    enriched: list[EnrichedTarget] = []
    for name, candidate, ot_model, hpa_model in zip(names, candidates, ot_models, hpa_models):
        claude_entry = synthesis_by_name.get(name.strip().upper(), {})
        scored_entry = score_by_name.get(name.strip().upper())

        enriched.append(EnrichedTarget(
            literature=candidate,
            opentargets=ot_model,
            hpa=hpa_model,
            integrated_confidence=claude_entry.get("integrated_confidence", "low"),
            integrated_rationale=claude_entry.get("integrated_rationale", ""),
            validation_summary=claude_entry.get("validation_summary", ""),
            consensus_score=round(scored_entry.consensus_score, 2) if scored_entry else None,
            methods_confirmed=scored_entry.appearances if scored_entry else 1,
        ))

    # Sort by integrated confidence then consensus score
    _conf_rank = {"high": 0, "medium": 1, "low": 2}
    enriched.sort(key=lambda e: (
        _conf_rank.get(e.integrated_confidence, 3),
        -(e.consensus_score or 0),
    ))

    return EnrichmentResult(
        original_query=request.original_query,
        enriched_targets=enriched,
        enrichment_summary=synthesis.get("enrichment_summary", ""),
        methods_used=["Literature Mining (PubMed + Claude)", "OpenTargets", "Human Protein Atlas"],
        targets_enriched=len(enriched),
        targets_not_found_in_ot=not_found_ot,
        targets_not_found_in_hpa=not_found_hpa,
    )
