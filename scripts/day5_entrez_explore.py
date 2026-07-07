# scripts/day5_entrez_explore.py
# Author: Boris Djagou
# Date: July 7, 2026
# Topic: Entrez API — exploring NCBI databases

from Bio import Entrez
import json

Entrez.email = "djagouboris@gmail.com"

# 1. List all available NCBI databases
print("=== Available NCBI Databases ===")
handle = Entrez.einfo()
record = Entrez.read(handle)
handle.close()
dbs = record["DbList"]
print(f"Total databases: {len(dbs)}")
print("Bioinformatics-relevant ones:")
relevant = ["nucleotide", "protein", "gene", "pubmed",
            "structure", "taxonomy", "sra", "assembly"]
for db in relevant:
    if db in dbs:
        print(f"  ✓ {db}")

# 2. Get details about the 'gene' database
print("\n=== Gene Database Info ===")
handle = Entrez.einfo(db="gene")
record = Entrez.read(handle)
handle.close()
print(f"Description : {record['DbInfo']['Description']}")
print(f"Record count: {int(record['DbInfo']['Count']):,}")
