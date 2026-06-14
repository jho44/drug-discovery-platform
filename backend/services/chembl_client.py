"""ChEMBL REST API client for known actives, similarity search, drug mechanisms, and fragment screening."""

from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import quote

import httpx

from config.settings import settings

_TIMEOUT = httpx.Timeout(30.0)


@dataclass
class ChEMBLCompound:
    compound_id: str
    name: Optional[str]
    smiles: Optional[str]
    mw: Optional[float]
    pchembl_value: Optional[float]
    image_url: str = field(default="")

    def __post_init__(self) -> None:
        self.image_url = f"{settings.chembl_api_url}/image/{self.compound_id}"


@dataclass
class DrugMechanism:
    drug_name: str
    chembl_drug_id: str
    max_phase: Optional[int]
    action_type: Optional[str]
    indication: Optional[str]


def _parse_float(val: object) -> Optional[float]:
    try:
        return float(val)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _parse_activity(raw: dict) -> Optional[ChEMBLCompound]:
    cid = raw.get("molecule_chembl_id")
    if not cid:
        return None
    return ChEMBLCompound(
        compound_id=cid,
        name=raw.get("molecule_pref_name"),
        smiles=raw.get("canonical_smiles"),
        mw=_parse_float((raw.get("molecule_properties") or {}).get("mw_freebase")),
        pchembl_value=_parse_float(raw.get("pchembl_value")),
    )


async def resolve_chembl_target(uniprot_id: str) -> Optional[str]:
    """Resolve a UniProt accession to a ChEMBL target ID."""
    url = f"{settings.chembl_api_url}/target"
    params = {
        "target_components__accession": uniprot_id,
        "format": "json",
        "limit": 1,
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            targets = resp.json().get("targets") or []
            return targets[0]["target_chembl_id"] if targets else None
    except Exception:
        return None


async def get_known_actives(chembl_id: str, limit: int = 20) -> list[ChEMBLCompound]:
    """Return compounds with pChEMBL >= 6 against the given ChEMBL target."""
    url = f"{settings.chembl_api_url}/activity"
    params = {
        "target_chembl_id": chembl_id,
        "pchembl_value__gte": 6,
        "format": "json",
        "limit": limit,
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            activities = resp.json().get("activities") or []
            return [c for raw in activities if (c := _parse_activity(raw)) is not None]
    except Exception:
        return []


async def get_similar_compounds(smiles: str, threshold: int = 70) -> list[ChEMBLCompound]:
    """Tanimoto similarity search against ChEMBL using Morgan fingerprints."""
    encoded = quote(smiles, safe="")
    url = f"{settings.chembl_api_url}/similarity/{encoded}/{threshold}"
    params = {"format": "json", "limit": 20}
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            molecules = resp.json().get("molecules") or []
            results = []
            for mol in molecules:
                cid = mol.get("molecule_chembl_id")
                if not cid:
                    continue
                structs = mol.get("molecule_structures") or {}
                props = mol.get("molecule_properties") or {}
                results.append(ChEMBLCompound(
                    compound_id=cid,
                    name=mol.get("pref_name"),
                    smiles=structs.get("canonical_smiles"),
                    mw=_parse_float(props.get("mw_freebase")),
                    pchembl_value=_parse_float(mol.get("similarity")),
                ))
            return results
    except Exception:
        return []


async def get_drug_mechanisms(chembl_id: str) -> list[DrugMechanism]:
    """Return known drug-target mechanisms for a ChEMBL target."""
    url = f"{settings.chembl_api_url}/mechanism"
    params = {"target_chembl_id": chembl_id, "format": "json", "limit": 20}
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            mechs = resp.json().get("mechanisms") or []
            results = []
            for m in mechs:
                drug_id = m.get("molecule_chembl_id")
                if not drug_id:
                    continue
                results.append(DrugMechanism(
                    drug_name=m.get("molecule_name") or drug_id,
                    chembl_drug_id=drug_id,
                    max_phase=m.get("max_phase"),
                    action_type=m.get("action_type"),
                    indication=None,
                ))
            return results
    except Exception:
        return []


async def get_fragment_actives(chembl_id: str) -> list[ChEMBLCompound]:
    """Return Rule-of-Three compliant fragments (MW ≤ 300, HBD ≤ 3) with activity against target."""
    url = f"{settings.chembl_api_url}/activity"
    params = {
        "target_chembl_id": chembl_id,
        "pchembl_value__gte": 4,
        "molecule_properties__mw_freebase__lte": 300,
        "molecule_properties__hbd__lte": 3,
        "format": "json",
        "limit": 20,
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            activities = resp.json().get("activities") or []
            return [c for raw in activities if (c := _parse_activity(raw)) is not None]
    except Exception:
        return []
