"""PubChem BioAssay REST client for HTS experimental results by target."""

from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Optional

import httpx

from config.settings import settings

_TIMEOUT = httpx.Timeout(30.0)


@dataclass
class PubChemAssay:
    aid: int
    name: str
    active_count: int


@dataclass
class PubChemCompound:
    cid: int
    name: Optional[str]
    smiles: Optional[str]
    mw: Optional[float]
    image_url: str = ""

    def __post_init__(self) -> None:
        self.image_url = f"{settings.pubchem_api_url}/compound/cid/{self.cid}/PNG"


async def get_hts_assays(uniprot_id: str, limit: int = 5) -> list[PubChemAssay]:
    """Return PubChem BioAssay IDs for assays targeting the given UniProt accession."""
    url = f"{settings.pubchem_api_url}/assay/target/UniProtID/{uniprot_id}/aids/JSON"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            aids = resp.json().get("IdentifierList", {}).get("AID") or []
            if not aids:
                return []

            # Fetch summaries for top N assays
            top_aids = aids[:limit]
            aid_str = ",".join(str(a) for a in top_aids)
            summary_url = f"{settings.pubchem_api_url}/assay/aid/{aid_str}/summary/JSON"
            s_resp = await client.get(summary_url)
            s_resp.raise_for_status()
            summaries = (
                s_resp.json()
                .get("AssaySummaries", {})
                .get("AssaySummary") or []
            )
            return [
                PubChemAssay(
                    aid=int(s.get("AID", 0)),
                    name=str(s.get("AssayName") or s.get("AID", "")),
                    active_count=int(s.get("ActiveCount") or 0),
                )
                for s in summaries
                if s.get("AID")
            ]
    except Exception:
        return []


async def get_assay_actives(aid: int, limit: int = 10) -> list[PubChemCompound]:
    """Return active compounds for a given BioAssay AID."""
    cids_url = f"{settings.pubchem_api_url}/assay/aid/{aid}/cids/JSON"
    params = {"sid_type": "active"}
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(cids_url, params=params)
            resp.raise_for_status()
            cids = resp.json().get("IdentifierList", {}).get("CID") or []
            if not cids:
                return []

            top_cids = cids[:limit]
            cid_str = ",".join(str(c) for c in top_cids)
            props_url = (
                f"{settings.pubchem_api_url}/compound/cid/{cid_str}"
                "/property/MolecularFormula,MolecularWeight,IUPACName,IsomericSMILES/JSON"
            )
            p_resp = await client.get(props_url)
            p_resp.raise_for_status()
            properties = p_resp.json().get("PropertyTable", {}).get("Properties") or []

            results = []
            for p in properties:
                cid = p.get("CID")
                if not cid:
                    continue
                mw_raw = p.get("MolecularWeight")
                try:
                    mw = float(mw_raw) if mw_raw is not None else None
                except (TypeError, ValueError):
                    mw = None
                results.append(PubChemCompound(
                    cid=int(cid),
                    name=p.get("IUPACName"),
                    smiles=p.get("IsomericSMILES"),
                    mw=mw,
                ))
            return results
    except Exception:
        return []
