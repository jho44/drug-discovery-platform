"""Fetch protein structure (PDB format) for a UniProt ID.

Priority: RCSB PDB experimental structure → AlphaFold predicted structure.
"""
from __future__ import annotations
import httpx

_UNIPROT_JSON = "https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
_RCSB_PDB_URL = "https://files.rcsb.org/download/{pdb_id}.pdb"
_ALPHAFOLD_URL = "https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"


async def _get_pdb_ids(uniprot_id: str, client: httpx.AsyncClient) -> list[str]:
    """Return PDB IDs cross-referenced in UniProt entry."""
    resp = await client.get(_UNIPROT_JSON.format(uniprot_id=uniprot_id))
    if resp.status_code != 200:
        return []
    data = resp.json()
    return [
        ref["id"]
        for ref in data.get("uniProtKBCrossReferences", [])
        if ref.get("database") == "PDB"
    ]


async def fetch_pdb_structure(uniprot_id: str) -> str | None:
    """Return PDB file text for the given UniProt ID.

    Tries RCSB experimental structures first (prefers the first PDB cross-
    reference from UniProt), then falls back to the AlphaFold model.
    Returns None if both sources are unavailable.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try RCSB experimental structure
        try:
            pdb_ids = await _get_pdb_ids(uniprot_id, client)
            print(f"[pdb] {uniprot_id}: found {len(pdb_ids)} PDB IDs: {pdb_ids[:5]}")
            for pdb_id in pdb_ids[:3]:  # try up to 3 in case some are unavailable
                resp = await client.get(_RCSB_PDB_URL.format(pdb_id=pdb_id))
                print(f"[pdb] {pdb_id}: status={resp.status_code} len={len(resp.text)}")
                if resp.status_code == 200 and resp.text.strip():
                    return resp.text
        except Exception as e:
            print(f"[pdb] RCSB fetch failed: {e}")

        # Fall back to AlphaFold
        try:
            resp = await client.get(_ALPHAFOLD_URL.format(uniprot_id=uniprot_id))
            print(f"[pdb] AlphaFold fallback: status={resp.status_code} len={len(resp.text)}")
            if resp.status_code == 200 and resp.text.strip():
                return resp.text
        except Exception as e:
            print(f"[pdb] AlphaFold fetch failed: {e}")

    print(f"[pdb] {uniprot_id}: no structure found")
    return None
