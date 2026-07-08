# scripts/day5_fetch_missing.py
# Author: Boris Djagou
# Date: July 7, 2026
# Fix: fetch kelch13 and dhfr by verified RefSeq accessions

from Bio import Entrez
import time

Entrez.email = "djagouboris@gmail.com"

# These accessions verified directly from PlasmoDB + NCBI RefSeq
MISSING = [
    {
        "name":        "kelch13",
        "locus_tag":   "PF3D7_1343700",
        "role":        "Artemisinin resistance",
        "note":        "C580Y, R539T mutations — artemisinin resistance marker",
        "search_query": "PF3D7_1343700[All Fields] AND Plasmodium falciparum[organism] AND refseq[filter]",
        "expected_aa": 726,
    },
    {
        "name":        "dhfr",
        "locus_tag":   "PF3D7_0417200",
        "role":        "Pyrimethamine resistance",
        "note":        "S108N mutation — bifunctional DHFR-TS enzyme",
        "search_query": "PF3D7_0417200[All Fields] AND Plasmodium falciparum[organism] AND refseq[filter]",
        "expected_aa": 608,
    },
]


def search_refseq(query, retmax=10):
    """Search NCBI protein database — RefSeq only."""
    handle = Entrez.esearch(db="protein", term=query, retmax=retmax)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]


def fetch_fasta(protein_id):
    """Fetch protein FASTA by NCBI ID."""
    handle = Entrez.efetch(db="protein", id=protein_id,
                           rettype="fasta", retmode="text")
    fasta = handle.read()
    handle.close()
    return fasta


def parse_fasta(fasta_text):
    """Parse single FASTA — return accession, description, sequence."""
    lines = fasta_text.strip().split("\n")
    header = lines[0][1:]
    seq    = "".join(lines[1:])
    parts  = header.split(" ", 1)
    acc    = parts[0]
    desc   = parts[1] if len(parts) > 1 else ""
    return acc, desc, seq


def main():
    print("\n🔬 Fixing kelch13 and dhfr — RefSeq search")
    print("=" * 55)

    for gene in MISSING:
        print(f"\n[{gene['name'].upper()}] — {gene['role']}")
        print(f"  Locus tag: {gene['locus_tag']}")
        print(f"  Expected : {gene['expected_aa']} aa")

        ids = search_refseq(gene["search_query"], retmax=10)
        print(f"  IDs found: {ids}")

        found = False
        for pid in ids:
            fasta = fetch_fasta(pid)
            acc, desc, seq = parse_fasta(fasta)
            length = len(seq)

            # Must be XP_ (RefSeq predicted) or NP_ (RefSeq curated)
            if not (acc.startswith("XP_") or acc.startswith("NP_")):
                print(f"  ⚠ Skipping {acc} — not a RefSeq accession")
                time.sleep(0.3)
                continue

            # Must contain Plasmodium
            if "Plasmodium" not in desc:
                print(f"  ⚠ Skipping {acc} — not Plasmodium")
                time.sleep(0.3)
                continue

            diff = abs(length - gene["expected_aa"])
            status = "✓ matches" if diff <= 50 else f"⚠ expected {gene['expected_aa']}"

            print(f"  ✅ Accession : {acc}")
            print(f"  Description  : {desc[:65]}...")
            print(f"  Length       : {length} aa  {status}")

            # Save FASTA
            path = f"results/day5_{gene['name']}_protein.fasta"
            with open(path, "w") as f:
                f.write(fasta)
            print(f"  Saved        : {path}")

            found = True
            break

        if not found:
            print(f"  ❌ Could not find RefSeq protein for {gene['name']}")
            print(f"  → Manual fallback: go to https://plasmodb.org/plasmo/app/record/gene/{gene['locus_tag']}")
            print(f"    Click 'Sequences' tab → copy protein FASTA manually")

        time.sleep(0.4)

    # Update combined FASTA with fixed proteins
    print("\n\nUpdating combined FASTA file...")
    genes_all = ["kelch13", "crt", "mdr1", "dhfr", "dhps"]
    combined  = "results/day5_all_resistance_proteins.fasta"
    written   = 0

    with open(combined, "w") as out:
        for g in genes_all:
            path = f"results/day5_{g}_protein.fasta"
            try:
                with open(path) as f:
                    content = f.read().strip()
                    if content:
                        out.write(content + "\n")
                        written += 1
                        print(f"  ✓ {g}")
            except FileNotFoundError:
                print(f"  ❌ Missing: {path}")

    print(f"\nCombined FASTA: {combined} ({written}/5 proteins)")
    print("=" * 55)


if __name__ == "__main__":
    main()
