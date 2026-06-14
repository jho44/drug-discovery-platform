"""OpenTargets Platform GraphQL client for genetic evidence and tractability data."""

from __future__ import annotations
import asyncio
import re
from dataclasses import dataclass

import httpx

from config.settings import settings

_TIMEOUT = httpx.Timeout(30.0)


@dataclass
class TractabilityScores:
    small_molecule: float | None
    antibody: float | None


@dataclass
class GeneticAssociation:
    disease_name: str
    score: float


@dataclass
class OpenTargetsResult:
    gene_symbol: str
    ensembl_id: str
    tractability: TractabilityScores
    top_genetic_associations: list[GeneticAssociation]
    mouse_phenotypes: list[str]
    safety_liabilities: list[str]


_RESOLVE_QUERY = """
query SearchTarget($query: String!) {
  search(queryString: $query, entityNames: ["target"], page: {index: 0, size: 1}) {
    hits {
      id
      name
    }
  }
}
"""

_TARGET_QUERY = """
query TargetData($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    approvedSymbol
    tractability {
      label
      modality
      value
    }
    associatedDiseases(page: {index: 0, size: 5}) {
      rows {
        disease {
          name
        }
        score
      }
    }
    mousePhenotypes(page: {index: 0, size: 10}) {
      rows {
        phenotypeName
      }
    }
    safetyLiabilities {
      event
    }
  }
}
"""


def _normalize_symbol(name: str) -> str:
    """Strip common variant suffixes (V600E, L858R) and return uppercase base symbol."""
    base = re.sub(r"[\s\-]?[A-Z]\d+[A-Z]?$", "", name.strip().upper())
    return base if base else name.strip().upper()


async def _resolve_ensembl_id(symbol: str, client: httpx.AsyncClient) -> str | None:
    try:
        resp = await client.post(
            settings.opentargets_graphql_url,
            json={"query": _RESOLVE_QUERY, "variables": {"query": symbol}},
        )
        resp.raise_for_status()
        hits = resp.json().get("data", {}).get("search", {}).get("hits", [])
        return hits[0]["id"] if hits else None
    except Exception:
        # Try first token before / or - for fusion genes / complexes
        fallback = re.split(r"[/\-]", symbol)[0]
        if fallback != symbol:
            return await _resolve_ensembl_id(fallback, client)
        return None


async def _fetch_target_data(
    gene_symbol: str,
    ensembl_id: str,
    client: httpx.AsyncClient,
) -> OpenTargetsResult | None:
    try:
        resp = await client.post(
            settings.opentargets_graphql_url,
            json={"query": _TARGET_QUERY, "variables": {"ensemblId": ensembl_id}},
        )
        resp.raise_for_status()
        data = resp.json().get("data", {}).get("target")
        if not data:
            return None

        # Tractability: extract smallMolecule and antibody modality max values
        sm_score: float | None = None
        ab_score: float | None = None
        for t in data.get("tractability") or []:
            modality = (t.get("modality") or "").lower()
            val = t.get("value")
            if val is True:
                val = 1.0
            elif val is False or val is None:
                continue
            try:
                val = float(val)
            except (TypeError, ValueError):
                continue
            if "small" in modality:
                sm_score = max(sm_score or 0.0, val)
            elif "antibody" in modality or "biologic" in modality:
                ab_score = max(ab_score or 0.0, val)

        associations = [
            GeneticAssociation(
                disease_name=row["disease"]["name"],
                score=round(row.get("score", 0.0), 3),
            )
            for row in (data.get("associatedDiseases") or {}).get("rows", [])
        ]

        phenotypes = [
            row["phenotypeName"]
            for row in (data.get("mousePhenotypes") or {}).get("rows", [])
            if row.get("phenotypeName")
        ]

        liabilities = [
            s["event"]
            for s in (data.get("safetyLiabilities") or [])
            if s.get("event")
        ]

        return OpenTargetsResult(
            gene_symbol=gene_symbol,
            ensembl_id=ensembl_id,
            tractability=TractabilityScores(small_molecule=sm_score, antibody=ab_score),
            top_genetic_associations=associations,
            mouse_phenotypes=phenotypes[:10],
            safety_liabilities=liabilities,
        )
    except Exception:
        return None


async def _get_one(symbol: str, client: httpx.AsyncClient) -> OpenTargetsResult | None:
    normalized = _normalize_symbol(symbol)
    ensembl_id = await _resolve_ensembl_id(normalized, client)
    if not ensembl_id:
        return None
    return await _fetch_target_data(symbol, ensembl_id, client)


async def get_opentargets_data(gene_symbols: list[str]) -> list[OpenTargetsResult | None]:
    """Fetch OpenTargets evidence for a list of gene symbols in parallel."""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        return list(await asyncio.gather(*(_get_one(sym, client) for sym in gene_symbols)))


# ---------------------------------------------------------------------------
# Known drugs — used by Stage 2 (Hit Discovery) for repurposing candidates
# ---------------------------------------------------------------------------

@dataclass
class KnownDrug:
    drug_id: str
    drug_name: str
    max_phase: int | None
    disease_name: str
    mechanism: str | None


_KNOWN_DRUGS_QUERY = """
query KnownDrugs($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    knownDrugs(size: 15) {
      rows {
        drug {
          id
          name
          maximumClinicalTrialPhase
        }
        disease {
          name
        }
        mechanismOfAction
      }
    }
  }
}
"""


async def _get_known_drugs_for_symbol(
    symbol: str, client: httpx.AsyncClient
) -> list[KnownDrug]:
    normalized = _normalize_symbol(symbol)
    ensembl_id = await _resolve_ensembl_id(normalized, client)
    if not ensembl_id:
        return []
    try:
        resp = await client.post(
            settings.opentargets_graphql_url,
            json={"query": _KNOWN_DRUGS_QUERY, "variables": {"ensemblId": ensembl_id}},
        )
        resp.raise_for_status()
        rows = (
            resp.json()
            .get("data", {})
            .get("target", {})
            .get("knownDrugs", {})
            .get("rows") or []
        )
        return [
            KnownDrug(
                drug_id=r["drug"]["id"],
                drug_name=r["drug"]["name"],
                max_phase=r["drug"].get("maximumClinicalTrialPhase"),
                disease_name=(r.get("disease") or {}).get("name", ""),
                mechanism=r.get("mechanismOfAction"),
            )
            for r in rows
            if r.get("drug", {}).get("id")
        ]
    except Exception:
        return []


async def get_known_drugs(gene_symbols: list[str]) -> dict[str, list[KnownDrug]]:
    """Fetch approved/clinical-stage drugs for each gene symbol via OpenTargets."""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        results = await asyncio.gather(
            *(_get_known_drugs_for_symbol(sym, client) for sym in gene_symbols)
        )
    return dict(zip(gene_symbols, results))
