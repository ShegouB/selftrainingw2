# scripts/day4_parse_genbank.py
# Author: Boris Djagou
# Date: July 6, 2026
# Exercise: Parse GenBank file — extract CDS annotations

from Bio import SeqIO

gbk_file = "data/pfalciparum_chr1.gbk"

print("Parsing GenBank file...")
record = SeqIO.read(gbk_file, "genbank")

print(f"\nOrganism : {record.annotations.get('organism', 'N/A')}")
print(f"Accession: {record.id}")
print(f"Length   : {len(record.seq):,} bp")
print(f"Features : {len(record.features)}")

# Extract CDS features
cds_list = [f for f in record.features if f.type == "CDS"]
print(f"CDS found: {len(cds_list)}")

print(f"\n{'Gene':<20} {'Start':>10} {'End':>10} {'Strand':>8} {'Product':<40}")
print("-" * 90)

for cds in cds_list[:20]:   # first 20 CDS
    gene = (cds.qualifiers.get("locus_tag") or
        cds.qualifiers.get("gene") or
        ["unknown"])[0]
    product = cds.qualifiers.get("product", ["unknown"])[0][:38]
    start   = int(cds.location.start)
    end     = int(cds.location.end)
    strand  = "+" if cds.location.strand == 1 else "-"
    print(f"{gene:<20} {start:>10,} {end:>10,} {strand:>8} {product:<40}")
