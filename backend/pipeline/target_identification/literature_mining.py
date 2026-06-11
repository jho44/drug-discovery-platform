"""Literature mining pipeline: PubMed search → Claude NER/relation extraction → candidate targets."""

from services.pubmed_client import search_pubmed, fetch_abstracts
from services.claude_client import analyze_abstracts_for_targets
from pipeline.target_identification.models import (
    LitMiningRequest,
    LitMiningResult,
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

    # 3. Send to Claude for analysis
    abstracts_payload = [
        {"pmid": a.pmid, "title": a.title, "abstract": a.abstract}
        for a in abstracts
    ]
    claude_result = await analyze_abstracts_for_targets(request.query, abstracts_payload)

    # 4. Build metadata list for display
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
        **claude_result,
    )
