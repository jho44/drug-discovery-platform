"""Stage 2 — Hit Identification orchestration.

Four parallel methods per target:
  1. Ligand-based: ChEMBL known actives + similarity search using top active SMILES
  2. Repurposing: ChEMBL drug mechanisms + OpenTargets known drugs
  3. Fragment screening: ChEMBL actives filtered by Rule of Three (MW≤300, HBD≤3)
  4. HTS experimental: PubChem BioAssay active compounds
"""

from __future__ import annotations
import asyncio

from pipeline.hit_discovery.models import (
    CompoundHit,
    HitDiscoveryRequest,
    HitDiscoveryResult,
    TargetHits,
)
from pipeline.target_identification.models import CandidateTarget
from services.chembl_client import (
    ChEMBLCompound,
    DrugMechanism,
    get_drug_mechanisms,
    get_fragment_actives,
    get_known_actives,
    get_similar_compounds,
    resolve_chembl_target,
)
from services.claude_client import synthesize_hit_discovery
from services.ensemble import compute_consensus
from services.opentargets_client import KnownDrug, get_known_drugs
from services.pubchem_client import PubChemCompound, get_assay_actives, get_hts_assays


async def _safe(coro):
    try:
        return await coro
    except Exception:
        return []


async def _empty():
    return []


def _chembl_to_hit(c: ChEMBLCompound, method: str) -> CompoundHit:
    return CompoundHit(
        compound_id=c.compound_id,
        name=c.name,
        smiles=c.smiles,
        molecular_weight=c.mw,
        method=method,
        source="ChEMBL",
        activity_value=c.pchembl_value,
        activity_unit="pChEMBL",
        image_url=c.image_url,
    )


def _drug_mech_to_hit(d: DrugMechanism) -> CompoundHit:
    return CompoundHit(
        compound_id=d.chembl_drug_id,
        name=d.drug_name,
        method="repurposing",
        source="ChEMBL",
        max_phase=d.max_phase,
        activity_value=None,
        image_url=f"https://www.ebi.ac.uk/chembl/api/data/image/{d.chembl_drug_id}",
    )


def _ot_drug_to_hit(d: KnownDrug) -> CompoundHit:
    return CompoundHit(
        compound_id=d.drug_id,
        name=d.drug_name,
        method="repurposing",
        source="OpenTargets",
        max_phase=d.max_phase,
        indication=d.disease_name or None,
        image_url=f"https://www.ebi.ac.uk/chembl/api/data/image/{d.drug_id}",
    )


def _pubchem_to_hit(c: PubChemCompound, assay_id: int) -> CompoundHit:
    return CompoundHit(
        compound_id=str(c.cid),
        name=c.name,
        smiles=c.smiles,
        molecular_weight=c.mw,
        method="hts",
        source="PubChem",
        assay_id=str(assay_id),
        image_url=c.image_url,
    )


def _hits_to_dicts(hits: list[CompoundHit]) -> list[dict]:
    return [{"compound_id": h.compound_id, **h.model_dump()} for h in hits]


async def _process_target(target: CandidateTarget) -> TargetHits:
    result = TargetHits(target_name=target.name, uniprot_id=target.uniprot_id)

    # Step 1: resolve ChEMBL target ID
    chembl_id: str | None = None
    if target.uniprot_id:
        chembl_id = await resolve_chembl_target(target.uniprot_id)
    result.chembl_target_id = chembl_id

    # Step 2: parallel fan-out across all methods
    (
        known_actives_raw,
        drug_mechs_raw,
        fragments_raw,
        ot_drugs_map,
        hts_assays_raw,
    ) = await asyncio.gather(
        _safe(get_known_actives(chembl_id)) if chembl_id else _empty(),
        _safe(get_drug_mechanisms(chembl_id)) if chembl_id else _empty(),
        _safe(get_fragment_actives(chembl_id)) if chembl_id else _empty(),
        _safe(get_known_drugs([target.name])),
        _safe(get_hts_assays(target.uniprot_id)) if target.uniprot_id else _empty(),
    )

    # Step 3: similarity search using top known active's SMILES (second phase)
    similarity_raw: list[ChEMBLCompound] = []
    if known_actives_raw:
        top_smiles = next((a.smiles for a in known_actives_raw if a.smiles), None)
        if top_smiles:
            similarity_raw = await _safe(get_similar_compounds(top_smiles))

    # Step 4: fetch PubChem assay actives (second phase, parallel across assays)
    hts_hits: list[CompoundHit] = []
    if hts_assays_raw:
        actives_results = await asyncio.gather(
            *[_safe(get_assay_actives(a.aid)) for a in hts_assays_raw[:2]]
        )
        for assay, actives in zip(hts_assays_raw[:2], actives_results):
            for c in actives:
                hts_hits.append(_pubchem_to_hit(c, assay.aid))

    # Step 5: build typed hit lists
    ot_drugs = (ot_drugs_map or {}).get(target.name, [])

    # Dedup known actives + similarity (same compound may appear in both)
    seen_ligand: set[str] = set()
    ligand_hits: list[CompoundHit] = []
    for c in list(known_actives_raw or []) + list(similarity_raw):
        if c.compound_id not in seen_ligand:
            seen_ligand.add(c.compound_id)
            ligand_hits.append(_chembl_to_hit(c, "ligand_similarity"))

    seen_repurposing: set[str] = set()
    repurposing_hits: list[CompoundHit] = []
    for d in drug_mechs_raw or []:
        if d.chembl_drug_id not in seen_repurposing:
            seen_repurposing.add(d.chembl_drug_id)
            repurposing_hits.append(_drug_mech_to_hit(d))
    for d in ot_drugs:
        if d.drug_id not in seen_repurposing:
            seen_repurposing.add(d.drug_id)
            repurposing_hits.append(_ot_drug_to_hit(d))

    fragment_hits = [_chembl_to_hit(c, "fragment") for c in (fragments_raw or [])]

    result.ligand_based_hits = ligand_hits
    result.repurposing_hits = repurposing_hits
    result.fragment_hits = fragment_hits
    result.hts_hits = hts_hits

    # Step 6: ensemble consensus across all methods
    all_method_dicts = [
        _hits_to_dicts(ligand_hits),
        _hits_to_dicts(repurposing_hits),
        _hits_to_dicts(fragment_hits),
        _hits_to_dicts(hts_hits),
    ]
    scored = compute_consensus(all_method_dicts, name_key="compound_id")

    # Rebuild top consensus hits with scores
    all_hits_by_id: dict[str, CompoundHit] = {}
    for h in ligand_hits + repurposing_hits + fragment_hits + hts_hits:
        if h.compound_id not in all_hits_by_id:
            all_hits_by_id[h.compound_id] = h

    consensus_hits: list[CompoundHit] = []
    for sc in scored[:20]:
        original_id = sc.method_results[0].get("compound_id", sc.name)
        hit = all_hits_by_id.get(original_id) or all_hits_by_id.get(sc.name)
        if hit:
            hit.consensus_score = round(sc.consensus_score, 3)
            consensus_hits.append(hit)
    result.consensus_hits = consensus_hits

    # Step 7: Claude synthesis
    methods_run = []
    if ligand_hits:
        methods_run.append("Ligand Similarity (ChEMBL)")
    if repurposing_hits:
        methods_run.append("Drug Repurposing")
    if fragment_hits:
        methods_run.append("Fragment Screening (ChEMBL)")
    if hts_hits:
        methods_run.append("HTS Experimental (PubChem)")

    result.methods_run = methods_run

    if any([ligand_hits, repurposing_hits, fragment_hits, hts_hits]):
        try:
            synthesis = await synthesize_hit_discovery(
                target_name=target.name,
                hits_by_method={
                    "ligand_similarity": [h.model_dump() for h in ligand_hits[:5]],
                    "repurposing": [h.model_dump() for h in repurposing_hits[:5]],
                    "fragment": [h.model_dump() for h in fragment_hits[:5]],
                    "hts": [h.model_dump() for h in hts_hits[:5]],
                },
            )
            result.claude_summary = synthesis.get("summary", "")
        except Exception:
            result.claude_summary = ""

    result.total_hits = len(
        set(
            h.compound_id
            for h in ligand_hits + repurposing_hits + fragment_hits + hts_hits
        )
    )
    return result


async def run_hit_identification(request: HitDiscoveryRequest) -> HitDiscoveryResult:
    """Run all four hit identification methods for each selected target."""
    target_results = await asyncio.gather(
        *(_process_target(t) for t in request.selected_targets)
    )

    all_methods: set[str] = set()
    for tr in target_results:
        all_methods.update(tr.methods_run)

    total_compounds = sum(tr.total_hits for tr in target_results)

    return HitDiscoveryResult(
        query_targets=[t.name for t in request.selected_targets],
        target_results=list(target_results),
        overall_summary=(
            f"Hit identification complete for {len(target_results)} target(s). "
            f"Found {total_compounds} unique compounds across "
            f"{len(all_methods)} method(s): {', '.join(sorted(all_methods))}."
        ),
        methods_used=sorted(all_methods),
        total_compounds_found=total_compounds,
    )
