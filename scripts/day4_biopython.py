# scripts/day4_biopython.py
# Author: Boris Djagou
# Date: July 6, 2026
# Topic: BioPython SeqIO — replacing our manual parser

from Bio import SeqIO
from Bio.SeqUtils import gc_fraction

genome_path = "data/pfalciparum_3D7_genome.fna"

print(f"{'ID':<15} {'Length (bp)':>12} {'GC%':>8}")
print("-" * 38)

for record in SeqIO.parse(genome_path, "fasta"):
    gc = round(gc_fraction(record.seq) * 100, 2)
    print(f"{record.id:<15} {len(record.seq):>12,} {gc:>8.2f}")

# Compare with your Day 2 manual script — results must be identical
