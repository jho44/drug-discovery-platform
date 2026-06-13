"""UniProt REST client for resolving gene symbols to UniProt accession IDs."""

from __future__ import annotations
import asyncio
import re
from dataclasses import dataclass

import httpx

_BASE = "https://rest.uniprot.org/uniprotkb/search"
_TIMEOUT = httpx.Timeout(15.0)
_HUMAN_TAXON = "9606"


@dataclass
class UniProtResult:
    accession: str          # e.g. "P15056"
    protein_name: str       # e.g. "Serine/threonine-protein kinase B-raf"
    gene_symbol: str        # primary gene symbol from UniProt


def _strip_variant(name: str) -> str:
    """Remove mutation suffixes like V600E, L858R so the symbol resolves cleanly."""
    return re.sub(r"[\s\-]?[A-Z]\d+[A-Z]?$", "", name.strip())


async def _resolve_one(gene_symbol: str, client: httpx.AsyncClient) -> UniProtResult | None:
    base_symbol = _strip_variant(gene_symbol)
    params = {
        "query": f"gene_exact:{base_symbol} AND organism_id:{_HUMAN_TAXON} AND reviewed:true",
        "format": "json",
        "fields": "accession,protein_name,gene_names",
        "size": "1",
    }
    try:
        resp = await client.get(_BASE, params=params)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            # Fallback: non-reviewed entries
            params["query"] = (
                f"gene_exact:{base_symbol} AND organism_id:{_HUMAN_TAXON}"
            )
            resp = await client.get(_BASE, params=params)
            resp.raise_for_status()
            results = resp.json().get("results", [])

        if not results:
            return None

        entry = results[0]
        accession = entry.get("primaryAccession", "")
        protein_desc = (
            entry.get("proteinDescription", {})
            .get("recommendedName", {})
            .get("fullName", {})
            .get("value", "")
        )
        genes = entry.get("genes", [])
        primary_gene = (
            genes[0].get("geneName", {}).get("value", base_symbol) if genes else base_symbol
        )
        return UniProtResult(
            accession=accession,
            protein_name=protein_desc,
            gene_symbol=primary_gene,
        )
    except Exception:
        return None


async def resolve_uniprot_ids(
    gene_symbols: list[str],
) -> dict[str, UniProtResult | None]:
    """Resolve a list of gene symbols to UniProt accessions in parallel.

    Returns a dict keyed by the original symbol (preserving input casing).
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        results = await asyncio.gather(*(_resolve_one(sym, client) for sym in gene_symbols))
    return dict(zip(gene_symbols, results))
