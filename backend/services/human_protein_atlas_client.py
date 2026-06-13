"""Human Protein Atlas REST client for tissue expression and pathology data."""

from __future__ import annotations
import asyncio
from dataclasses import dataclass, field

import httpx

from config.settings import settings

_TIMEOUT = httpx.Timeout(30.0)


@dataclass
class TissueExpression:
    tissue: str
    rna_level: str  # "High" | "Medium" | "Low" | "Not detected"


@dataclass
class CancerPathology:
    cancer_type: str
    high_expression_percent: float
    survival_correlation: str | None  # "favorable" | "unfavorable" | None


@dataclass
class HPAResult:
    gene_symbol: str
    protein_class: list[str]
    tissue_expression: list[TissueExpression]
    cancer_pathology: list[CancerPathology]
    subcellular_locations: list[str]
    hpa_url: str


def _parse_hpa_json(gene_symbol: str, data: dict) -> HPAResult:
    hpa_url = f"{settings.hpa_base_url}/{gene_symbol}"

    # Protein class
    protein_class = [
        c.strip()
        for c in str(data.get("Protein class", "")).split(",")
        if c.strip()
    ]

    # Tissue RNA expression — HPA returns a list of dicts or a summary string
    tissue_expression: list[TissueExpression] = []
    rna_data = data.get("RNA tissue overview") or data.get("RNA tissue category") or []
    if isinstance(rna_data, list):
        for entry in rna_data:
            tissue = entry.get("tissue") or entry.get("Tissue") or ""
            level = entry.get("level") or entry.get("Level") or "Not detected"
            if tissue:
                tissue_expression.append(TissueExpression(tissue=tissue, rna_level=level))
    elif isinstance(rna_data, dict):
        for tissue, level in rna_data.items():
            tissue_expression.append(TissueExpression(tissue=tissue, rna_level=str(level)))

    # Cancer pathology
    cancer_pathology: list[CancerPathology] = []
    pathology_data = data.get("Pathology") or data.get("pathology") or []
    if isinstance(pathology_data, list):
        for entry in pathology_data:
            cancer_type = entry.get("Cancer") or entry.get("cancer") or ""
            if not cancer_type:
                continue
            high_pct = float(entry.get("High", entry.get("high", 0)) or 0)
            prog = entry.get("prognostic - favorable") or entry.get("prognostic - unfavorable")
            if entry.get("prognostic - favorable"):
                correlation = "favorable"
            elif entry.get("prognostic - unfavorable"):
                correlation = "unfavorable"
            else:
                correlation = None
            cancer_pathology.append(CancerPathology(
                cancer_type=cancer_type,
                high_expression_percent=high_pct,
                survival_correlation=correlation,
            ))

    # Subcellular locations
    locations_raw = data.get("Subcellular location") or data.get("subcellular_location") or []
    if isinstance(locations_raw, list):
        subcellular_locations = [str(loc) for loc in locations_raw if loc]
    elif isinstance(locations_raw, str):
        subcellular_locations = [l.strip() for l in locations_raw.split(",") if l.strip()]
    else:
        subcellular_locations = []

    return HPAResult(
        gene_symbol=gene_symbol,
        protein_class=protein_class,
        tissue_expression=tissue_expression,
        cancer_pathology=cancer_pathology,
        subcellular_locations=subcellular_locations,
        hpa_url=hpa_url,
    )


async def _fetch_one(gene_symbol: str, client: httpx.AsyncClient) -> HPAResult | None:
    url = f"{settings.hpa_base_url}/{gene_symbol.upper()}.json"
    try:
        resp = await client.get(url)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        # HPA returns either a dict or a list with one entry
        if isinstance(data, list):
            data = data[0] if data else {}
        return _parse_hpa_json(gene_symbol, data)
    except Exception:
        return None


async def get_hpa_data(gene_symbols: list[str]) -> list[HPAResult | None]:
    """Fetch Human Protein Atlas data for a list of gene symbols in parallel."""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        return list(await asyncio.gather(*(_fetch_one(sym, client) for sym in gene_symbols)))
