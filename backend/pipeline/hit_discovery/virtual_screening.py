"""Virtual screening via AutoDock Vina.

Pipeline: fetch receptor PDB → prepare receptor PDBQT → for each compound
SMILES: generate 3D conformer with RDKit → prepare ligand PDBQT with Meeko →
dock with Vina → collect scores → sort ascending (most negative = best).
"""
from __future__ import annotations

import asyncio
import copy
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor

from pipeline.hit_discovery.models import CompoundHit
from services.pdb_client import fetch_pdb_structure

_EXECUTOR = ThreadPoolExecutor(max_workers=2)


def _prepare_receptor_pdbqt(pdb_string: str, tmpdir: str) -> str | None:
    """Prepare receptor PDBQT by calling mk_prepare_receptor.py (ships with meeko).

    This is the direct successor to prepare_receptor4.py from MGLTools —
    handles atom typing, rotatable OH/NH groups, and Gasteiger charges.
    """
    import subprocess
    import sys

    pdb_path = os.path.join(tmpdir, "receptor.pdb")
    pdbqt_path = os.path.join(tmpdir, "receptor.pdbqt")

    # Strip HETATM records (co-crystallized ligands, waters, ions) — keep only protein ATOM lines
    clean_pdb = "\n".join(
        line for line in pdb_string.splitlines()
        if line.startswith(("ATOM", "TER", "END"))
    )
    with open(pdb_path, "w") as f:
        f.write(clean_pdb)

    # mk_prepare_receptor.py is installed into the same bin as the current Python
    script = os.path.join(os.path.dirname(sys.executable), "mk_prepare_receptor.py")
    cmd = [sys.executable, script, "-i", pdb_path, "-o", pdbqt_path, "-a"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"[vina] mk_prepare_receptor exit={result.returncode}")
    if result.stdout:
        print(f"[vina] mk_prepare_receptor stdout: {result.stdout[:300]}")
    if result.stderr:
        print(f"[vina] mk_prepare_receptor stderr: {result.stderr[:300]}")

    if result.returncode != 0 or not os.path.exists(pdbqt_path):
        return None

    with open(pdbqt_path) as f:
        pdbqt = f.read()
    print(f"[vina] receptor PDBQT ready ({len(pdbqt)} chars)")
    return pdbqt


def _get_centroid(pdb_string: str) -> tuple[float, float, float]:
    """Return geometric centroid of Cα atoms (all ATOM atoms as fallback)."""
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for raw in pdb_string.splitlines():
        if not raw.startswith("ATOM"):
            continue
        if raw[12:16].strip() != "CA":
            continue
        try:
            xs.append(float(raw[30:38]))
            ys.append(float(raw[38:46]))
            zs.append(float(raw[46:54]))
        except ValueError:
            continue
    if not xs:
        for raw in pdb_string.splitlines():
            if not raw.startswith("ATOM"):
                continue
            try:
                xs.append(float(raw[30:38]))
                ys.append(float(raw[38:46]))
                zs.append(float(raw[46:54]))
            except ValueError:
                continue
    if not xs:
        return 0.0, 0.0, 0.0
    return sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)


def _smiles_to_pdbqt(smiles: str) -> str | None:
    """Generate 3D conformer from SMILES and return Meeko PDBQT string."""
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        from meeko import MoleculePreparation, PDBQTWriterLegacy

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"[vina] invalid SMILES: {smiles[:40]}")
            return None
        mol = Chem.AddHs(mol)
        params = AllChem.ETKDGv3()
        params.randomSeed = 42
        if AllChem.EmbedMolecule(mol, params) != 0:
            # ETKDGv3 failed; try simpler embedding
            if AllChem.EmbedMolecule(mol) != 0:
                print(f"[vina] 3D embedding failed: {smiles[:40]}")
                return None
        AllChem.MMFFOptimizeMolecule(mol)

        preparator = MoleculePreparation()
        mol_setups = preparator.prepare(mol)
        if not mol_setups:
            print(f"[vina] meeko prep failed: {smiles[:40]}")
            return None
        pdbqt_string, success, err = PDBQTWriterLegacy.write_string(mol_setups[0])
        if not success:
            print(f"[vina] PDBQT write failed ({err}): {smiles[:40]}")
        return pdbqt_string if success else None
    except Exception as e:
        print(f"[vina] _smiles_to_pdbqt exception: {e}")
        return None


def _dock_one(
    rec_path: str,
    ligand_pdbqt: str,
    center: tuple[float, float, float],
    box_size: list[float],
    tmpdir: str,
    idx: int,
) -> float | None:
    """Write ligand PDBQT, run Vina, return best docking score or None."""
    try:
        from vina import Vina

        lig_path = os.path.join(tmpdir, f"lig_{idx}.pdbqt")
        with open(lig_path, "w") as f:
            f.write(ligand_pdbqt)

        v = Vina(sf_name="vina", verbosity=0)
        v.set_receptor(rec_path)
        v.set_ligand_from_file(lig_path)
        v.compute_vina_maps(center=list(center), box_size=box_size)
        v.dock(exhaustiveness=8, n_poses=1)
        energies = v.energies(n_poses=1)
        if energies and energies[0]:
            score = float(energies[0][0])
            print(f"[vina] lig_{idx}: score={score}")
            return score
    except Exception as e:
        print(f"[vina] lig_{idx} dock failed: {e}")
    return None


def _run_docking_sync(
    pdb_string: str,
    hits: list[CompoundHit],
) -> list[CompoundHit]:
    """Prepare receptor, dock each hit, return hits with docking_score set."""
    center = _get_centroid(pdb_string)
    box_size = [22.0, 22.0, 22.0]
    print(f"[vina] box center={center} size={box_size}")

    results: list[CompoundHit] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        receptor_pdbqt = _prepare_receptor_pdbqt(pdb_string, tmpdir)
        if receptor_pdbqt is None:
            return []
        rec_path = os.path.join(tmpdir, "receptor.pdbqt")

        for idx, hit in enumerate(hits):
            if not hit.smiles:
                continue
            ligand_pdbqt = _smiles_to_pdbqt(hit.smiles)
            if ligand_pdbqt is None:
                continue
            score = _dock_one(rec_path, ligand_pdbqt, center, box_size, tmpdir, idx)
            if score is not None:
                docked = copy.copy(hit)
                docked.docking_score = round(score, 2)
                results.append(docked)

    results.sort(key=lambda h: h.docking_score)  # most negative (best) first
    return results


async def dock_compounds(
    uniprot_id: str,
    hits: list[CompoundHit],
    max_compounds: int = 10,
) -> list[CompoundHit]:
    """Dock up to max_compounds consensus hits against the target structure.

    Fetches the receptor PDB (experimental from RCSB, or AlphaFold fallback),
    runs AutoDock Vina for each compound with a SMILES, and returns a list
    ranked by docking score ascending (kcal/mol — most negative = tightest fit).
    """
    pdb_string = await fetch_pdb_structure(uniprot_id)
    if not pdb_string:
        return []

    candidates = [h for h in hits if h.smiles][:max_compounds]
    if not candidates:
        return []

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_EXECUTOR, _run_docking_sync, pdb_string, candidates)
