"""Literature mining pipeline: PubMed search → Claude NER/relation extraction → candidate targets."""

from __future__ import annotations
from services.pubmed_client import search_pubmed, fetch_abstracts
from services.claude_client import analyze_abstracts_for_targets
from services.uniprot_client import resolve_uniprot_ids
from pipeline.target_identification.models import (
    LitMiningRequest,
    LitMiningResult,
    CandidateTarget,
    AbstractMeta,
)


async def run_literature_mining(request: LitMiningRequest) -> LitMiningResult:
    # 1. Search PubMed for relevant PMIDs
    pmids = await search_pubmed(request.query, max_results=request.max_abstracts)

    if not pmids:
        return LitMiningResult(
            query=request.query,
            abstracts_fetched=0,
            abstracts_meta=[],
            entities={"genes_proteins": [], "diseases": []},
            relations=[],
            candidate_targets=[],
            summary="No abstracts found for this query. Try a more specific search term.",
        )

    # 2. Fetch full abstracts
    abstracts = await fetch_abstracts(pmids)

    # 3. Claude: NER, relation extraction, candidate target identification
    abstracts_payload = [
        {"pmid": a.pmid, "title": a.title, "abstract": a.abstract}
        for a in abstracts
    ]
    claude_result = await analyze_abstracts_for_targets(request.query, abstracts_payload)

    # 4. Resolve UniProt IDs for all candidate gene/protein targets in parallel
    raw_candidates = claude_result.get("candidate_targets", [])
    gene_names = [c["name"] for c in raw_candidates if c.get("type") in ("gene", "protein")]
    uniprot_map = await resolve_uniprot_ids(gene_names) if gene_names else {}

    enriched_candidates = []
    for c in raw_candidates:
        uniprot = uniprot_map.get(c["name"])
        enriched_candidates.append(
            CandidateTarget(
                **{k: v for k, v in c.items() if k not in ("uniprot_id", "uniprot_name")},
                uniprot_id=uniprot.accession if uniprot else None,
                uniprot_name=uniprot.protein_name if uniprot else None,
            )
        )

    # 5. Build metadata list for display
    abstracts_meta = [
        AbstractMeta(
            pmid=a.pmid,
            title=a.title,
            authors=a.authors,
            journal=a.journal,
            year=a.year,
        )
        for a in abstracts
    ]

    return LitMiningResult(
        query=request.query,
        abstracts_fetched=len(abstracts),
        abstracts_meta=abstracts_meta,
        entities=claude_result.get("entities", {"genes_proteins": [], "diseases": []}),
        relations=claude_result.get("relations", []),
        candidate_targets=enriched_candidates,
        summary=claude_result.get("summary", ""),
    )
