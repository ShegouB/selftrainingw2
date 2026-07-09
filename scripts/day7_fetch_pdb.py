# scripts/day7_fetch_pdb.py
# Author: Boris Djagou
# Date: July 9, 2026
# Topic: Fetch PDB structures for M. tuberculosis drug targets

import requests
import os
import time

PDB_DOWNLOAD = "https://files.rcsb.org/download"
PDB_API      = "https://data.rcsb.org/rest/v1/core/entry"

# PDB IDs for your Day 6 drug targets — verified from RCSB
STRUCTURES = [
    {
        "pdb_id":   "1P44",
        "gene":     "inhA",
        "drug":     "Isoniazid",
        "organism": "M. tuberculosis",
        "note":     "InhA with bound NADH cofactor — drug binding site",
    },
    {
        "pdb_id":   "2X23",
        "gene":     "inhA",
        "drug":     "Ethionamide (inhibitor)",
        "organism": "M. tuberculosis",
        "note":     "InhA with ethionamide-NAD adduct — shows resistance mechanism",
    },
    {
        "pdb_id":   "3IFZ",
        "gene":     "gyrA",
        "drug":     "Fluoroquinolones",
        "organism": "M. tuberculosis",
        "note":     "GyrA TOPRIM domain — fluoroquinolone binding region",
    },
    {
        "pdb_id":   "3PL1",
        "gene":     "katG",
        "drug":     "Isoniazid (activator)",
        "organism": "M. tuberculosis",
        "note":     "KatG catalase-peroxidase — activates isoniazid prodrug",
    },
    {
        "pdb_id":   "3RGK",
        "gene":     "pncA",
        "drug":     "Pyrazinamide",
        "organism": "M. tuberculosis",
        "note":     "PncA nicotinamidase — converts pyrazinamide to active form",
    },
]


def fetch_pdb_metadata(pdb_id):
    """Fetch PDB entry metadata from RCSB REST API."""
    r = requests.get(f"{PDB_API}/{pdb_id.lower()}")
    if r.status_code == 200:
        return r.json()
    return {}


def download_pdb(pdb_id, output_dir="data/pdb"):
    """Download PDB file from RCSB."""
    url      = f"{PDB_DOWNLOAD}/{pdb_id.upper()}.pdb"
    filepath = os.path.join(output_dir, f"{pdb_id.lower()}.pdb")

    if os.path.exists(filepath):
        print(f"  Already downloaded: {filepath}")
        return filepath

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(filepath, "w") as f:
            f.write(r.text)
        size = os.path.getsize(filepath)
        print(f"  Downloaded: {filepath} ({size/1024:.1f} KB)")
        return filepath
    else:
        print(f"  ❌ Failed to download {pdb_id}: HTTP {r.status_code}")
        return None


def main():
    print("\n🔬 Day 7 — Fetching PDB Structures for TB Drug Targets")
    print("=" * 62)

    os.makedirs("data/pdb", exist_ok=True)

    for struct in STRUCTURES:
        pdb_id = struct["pdb_id"]
        print(f"\n[{pdb_id}] {struct['gene'].upper()} — {struct['drug']}")
        print(f"  Note: {struct['note']}")

        # Get metadata
        meta = fetch_pdb_metadata(pdb_id)
        if meta:
            title   = meta.get("struct", {}).get("title", "N/A")
            method  = meta.get("exptl", [{}])[0].get("method", "N/A")
            res_val = meta.get("refine", [{}])[0].get("ls_d_res_high", None) \
                      if meta.get("refine") else None
            release = meta.get("rcsb_accession_info", {}).get("initial_release_date", "N/A")[:10]

            print(f"  Title      : {title[:60]}...")
            print(f"  Method     : {method}")
            if res_val:
                print(f"  Resolution : {res_val} Å")
            print(f"  Released   : {release}")

        # Download
        path = download_pdb(pdb_id)
        time.sleep(0.5)

    print("\n\n=== Downloaded PDB files ===")
    for f in sorted(os.listdir("data/pdb")):
        if f.endswith(".pdb"):
            size = os.path.getsize(f"data/pdb/{f}")
            print(f"  {f:<20} {size/1024:>8.1f} KB")

    print("\n✅ PDB download complete!")
    print("=" * 62)


if __name__ == "__main__":
    main()
