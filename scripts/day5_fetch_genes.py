# scripts/day5_fetch_genes.py
# Author: Boris Djagou
# Date: July 7, 2026
# Fixed version — fetch by direct protein accession numbers

from Bio import Entrez, SeqIO
import csv
import time

Entrez.email = "djagouboris@gmail.com"

# Direct accession numbers — always work
GENES = [
    {
        "name":    "kelch13",
        "accession": "XP_001351443",
        "role":    "Artemisinin resistance",
        "note":    "Mutations C580Y, R539T cause artemisinin resistance",
    },
    {
        "name":    "crt",
        "accession": "XP_001347509",
        "role":    "Chloroquine resistance",
        "note":    "K76T mutation causes chloroquine resistance",
    },
    {
        "name":    "mdr1",
        "accession": "XP_001350763",
        "role":    "Multidrug resistance",
        "note":    "N86Y mutation affects lumefantrine susceptibility",
    },
    {
        "name":    "dhfr",
        "accession": "XP_966441",
        "role":    "Pyrimethamine resistance",
        "note":    "S108N mutation — first step to resistance",
    },
    {
        "name":    "dhps",
        "accession": "XP_001350938",
        "role":    "Sulfadoxine resistance",
        "note":    "A437G + K540E mutations cause sulfadoxine resistance",
    },
]


def fetch_protein(accession):
    """Fetch protein record by accession number."""
    handle = Entrez.efetch(
        db="protein",
        id=accession,
        rettype="fasta",
        retmode="text"
    )
    fasta = handle.read()
    handle.close()
    return fasta


def parse_fasta_single(fasta_text):
    """Parse a single FASTA record — return header and sequence."""
    lines  = fasta_text.strip().split("\n")
    header = lines[0][1:]          # remove >
    seq    = "".join(lines[1:])
    return header, seq


def main():
    print("\n Day 5 v2 — Fetching 5 P. falciparum Resistance Gene Proteins")
    print("=" * 65)

    results = []

    for gene in GENES:
        print(f"\n[Fetching] {gene['name'].upper()} — {gene['role']}")
        print(f"  Accession: {gene['accession']}")
        print(f"  Note     : {gene['note']}")

        fasta = fetch_protein(gene["accession"])
        header, seq = parse_fasta_single(fasta)

        length = len(seq)
        gc_na  = "N/A"   # proteins have no GC content

        print(f"  Length   : {length} amino acids")
        print(f"  Header   : {header[:65]}...")

        # Save individual FASTA
        fasta_path = f"results/day5_{gene['name']}_protein.fasta"
        with open(fasta_path, "w") as f:
            f.write(fasta)
        print(f"  Saved    : {fasta_path}")

        results.append({
            "gene":       gene["name"],
            "accession":  gene["accession"],
            "role":       gene["role"],
            "length_aa":  length,
            "note":       gene["note"],
            "header":     header[:80],
        })

        time.sleep(0.4)   # NCBI rate limit

    # Print summary table
    print("\n\n=== Summary — 5 Resistance Gene Proteins ===")
    print(f"{'Gene':<10} {'Accession':<15} {'Length (aa)':>12} {'Role':<30}")
    print("-" * 70)
    for r in results:
        print(f"{r['gene']:<10} {r['accession']:<15} "
              f"{r['length_aa']:>12,} {r['role']:<30}")

    # Export CSV
    csv_path = "results/day5_resistance_genes.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nCSV saved : {csv_path}")

    # Save all sequences in one combined FASTA
    combined_path = "results/day5_all_resistance_proteins.fasta"
    with open(combined_path, "w") as f:
        for gene in GENES:
            individual = f"results/day5_{gene['name']}_protein.fasta"
            with open(individual) as g:
                f.write(g.read())
    print(f"Combined  : {combined_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
