# scripts/day7_parse_pdb.py
# Author: Boris Djagou
# Date: July 9, 2026
# Topic: Parse PDB files — chains, residues, ligands, active sites

from Bio.PDB import PDBParser, DSSP
from Bio.PDB.Polypeptide import is_aa
import warnings
import csv
import os

warnings.filterwarnings("ignore")   # suppress PDB warnings

PDB_DIR = "data/pdb"

STRUCTURES = [
    {"pdb_id": "1p44", "gene": "inhA",  "drug": "Isoniazid/NADH"},
    {"pdb_id": "2x23", "gene": "inhA",  "drug": "Ethionamide-NAD adduct"},
    {"pdb_id": "3ifl", "gene": "gyrA",  "drug": "Fluoroquinolones"},
    {"pdb_id": "3pl1", "gene": "katG",  "drug": "Isoniazid activator"},
    {"pdb_id": "3rgk", "gene": "pncA",  "drug": "Pyrazinamide"},
]


def parse_structure(pdb_file, pdb_id):
    """Parse a PDB file and return structure object."""
    parser = PDBParser(QUIET=True)
    return parser.get_structure(pdb_id, pdb_file)


def get_chains_info(structure):
    """Extract chain information from structure."""
    model  = structure[0]
    chains = []
    for chain in model:
        residues = list(chain.get_residues())
        aa_count  = sum(1 for r in residues if is_aa(r))
        het_count = sum(1 for r in residues
                       if r.id[0] != " " and r.id[0] != "W")
        wat_count = sum(1 for r in residues if r.id[0] == "W")
        chains.append({
            "chain_id":  chain.id,
            "residues":  len(residues),
            "aa":        aa_count,
            "ligands":   het_count,
            "waters":    wat_count,
        })
    return chains


def get_ligands(structure):
    """Extract non-water HETATM ligands."""
    ligands = []
    for residue in structure[0].get_residues():
        # HETATM records have id[0] != ' ' and not water
        if residue.id[0] not in (" ", "W"):
            resname = residue.resname.strip()
            chain   = residue.get_parent().id
            resnum  = residue.id[1]
            atoms   = list(residue.get_atoms())
            ligands.append({
                "name":    resname,
                "chain":   chain,
                "resnum":  resnum,
                "n_atoms": len(atoms),
            })
    return ligands


def get_bfactors(structure, chain_id="A"):
    """Get B-factors (temperature factors) for chain A — flexibility indicator."""
    bfactors = []
    model    = structure[0]
    if chain_id not in [c.id for c in model]:
        return []
    for residue in model[chain_id].get_residues():
        if is_aa(residue):
            # Use CA atom B-factor
            if "CA" in residue:
                bf = residue["CA"].get_bfactor()
                bfactors.append({
                    "resnum":   residue.id[1],
                    "resname":  residue.resname,
                    "bfactor":  round(bf, 2),
                })
    return bfactors


def find_active_site_residues(structure, known_positions, chain_id="A"):
    """Find residues near known active site positions."""
    model = structure[0]
    if chain_id not in [c.id for c in model]:
        return []
    found = []
    for residue in model[chain_id].get_residues():
        if residue.id[1] in known_positions and is_aa(residue):
            found.append(f"{residue.resname}{residue.id[1]}")
    return found


def main():
    print("\n🔬 Day 7 — Parsing PDB Structures")
    print("=" * 65)

    all_results = []

    for s in STRUCTURES:
        pdb_file = os.path.join(PDB_DIR, f"{s['pdb_id']}.pdb")

        # Try uppercase filename too
        if not os.path.exists(pdb_file):
            pdb_file = os.path.join(PDB_DIR, f"{s['pdb_id'].upper()}.pdb")

        if not os.path.exists(pdb_file):
            print(f"\n[{s['pdb_id'].upper()}] ❌ File not found — skip")
            continue

        print(f"\n{'='*65}")
        print(f"[{s['pdb_id'].upper()}] {s['gene'].upper()} — {s['drug']}")

        structure = parse_structure(pdb_file, s["pdb_id"])
        chains    = get_chains_info(structure)
        ligands   = get_ligands(structure)
        bfactors  = get_bfactors(structure, "A")

        # Chain summary
        print(f"\n  Chains ({len(chains)}):")
        print(f"  {'Chain':>6} {'Total res':>10} {'AA':>6} "
              f"{'Ligands':>8} {'Waters':>7}")
        print("  " + "-" * 42)
        for c in chains:
            print(f"  {c['chain_id']:>6} {c['residues']:>10} {c['aa']:>6} "
                  f"{c['ligands']:>8} {c['waters']:>7}")

        # Ligands
        if ligands:
            print(f"\n  Ligands / Cofactors ({len(ligands)}):")
            for lig in ligands:
                print(f"    {lig['name']:<6} chain {lig['chain']} "
                      f"res {lig['resnum']:>4} — {lig['n_atoms']} atoms")

        # B-factor stats (flexibility)
        if bfactors:
            bvals = [r["bfactor"] for r in bfactors]
            avg_b = sum(bvals) / len(bvals)
            max_b = max(bvals)
            max_r = [r for r in bfactors if r["bfactor"] == max_b][0]
            min_b = min(bvals)

            print(f"\n  Chain A B-factors (flexibility):")
            print(f"    Residues: {len(bfactors)}")
            print(f"    Avg     : {avg_b:.2f} Å²")
            print(f"    Min     : {min_b:.2f} Å²  (rigid)")
            print(f"    Max     : {max_b:.2f} Å²  "
                  f"(most flexible: {max_r['resname']}{max_r['resnum']})")

        # Total atoms
        n_atoms = sum(1 for _ in structure.get_atoms())
        print(f"\n  Total atoms in structure: {n_atoms:,}")

        all_results.append({
            "pdb_id":    s["pdb_id"].upper(),
            "gene":      s["gene"],
            "drug":      s["drug"],
            "n_chains":  len(chains),
            "n_aa":      sum(c["aa"] for c in chains),
            "n_ligands": len(ligands),
            "n_atoms":   n_atoms,
            "ligand_names": " | ".join(
                set(l["name"] for l in ligands)
            ),
        })

    # Summary table
    print(f"\n\n{'='*65}")
    print("SUMMARY — PDB Structures Parsed")
    print(f"{'='*65}")
    print(f"  {'PDB':>6} {'Gene':<8} {'Chains':>7} {'AA':>6} "
          f"{'Ligands':>8} {'Atoms':>8}  Ligand names")
    print("  " + "-" * 80)
    for r in all_results:
        print(f"  {r['pdb_id']:>6} {r['gene']:<8} {r['n_chains']:>7} "
              f"{r['n_aa']:>6,} {r['n_ligands']:>8} {r['n_atoms']:>8,}  "
              f"{r['ligand_names'][:30]}")

    # Export
    if all_results:
        csv_path = "results/day7_pdb_structures.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n  CSV saved: {csv_path}")

    print("\n✅ Day 7 parsing complete!")
    print("=" * 65)


if __name__ == "__main__":
    main()
