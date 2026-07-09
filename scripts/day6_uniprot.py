# scripts/day6_uniprot.py
# Author: Boris Djagou
# Date: July 8, 2026
# Topic: UniProt REST API — M. tuberculosis & P. falciparum proteins

import requests
import csv
import time
import json

BASE = "https://rest.uniprot.org/uniprotkb/search"


def count_proteins(query):
    """Return total number of proteins matching a query."""
    r = requests.get(BASE, params={
        "query": query, "format": "json", "size": 1
    })
    return r.headers.get("X-Total-Results", "0")


def fetch_proteins(query, fields, size=20):
    """Fetch proteins with selected fields. Returns list of dicts."""
    params = {
        "query":  query,
        "format": "json",
        "size":   size,
        "fields": fields,
    }
    r = requests.get(BASE, params=params)
    r.raise_for_status()
    data = r.json()
    return data.get("results", [])


def parse_entry(entry):
    """Extract key fields from a UniProt JSON entry."""
    acc     = entry.get("primaryAccession", "")
    name    = entry.get("uniProtkbId",      "")

    # Protein full name
    prot    = entry.get("proteinDescription", {})
    rec     = prot.get("recommendedName", {})
    fullname= rec.get("fullName", {}).get("value", "unknown") if rec \
              else prot.get("submissionNames", [{}])[0]\
                       .get("fullName", {}).get("value", "unknown")

    # Gene name
    genes   = entry.get("genes", [{}])
    gene    = genes[0].get("geneName", {}).get("value", "unknown") \
              if genes else "unknown"

    # Sequence length
    seq     = entry.get("sequence", {})
    length  = seq.get("length", 0)

    # Function annotation
    comments = entry.get("comments", [])
    function = ""
    for c in comments:
        if c.get("commentType") == "FUNCTION":
            texts = c.get("texts", [])
            if texts:
                function = texts[0].get("value", "")[:120]
            break

    # Keywords
    keywords = [k.get("name","") for k in entry.get("keywords", [])][:5]

    return {
        "accession": acc,
        "entry_name": name,
        "gene":      gene,
        "protein":   fullname,
        "length_aa": length,
        "function":  function,
        "keywords":  " | ".join(keywords),
    }


def main():
    print("\n🧬 Day 6 — UniProt REST API")
    print("=" * 65)

    # ── SECTION 1: Database counts ──────────────────────────────────
    print("\n[1/4] Protein counts in UniProt Swiss-Prot")
    print("-" * 45)

    organisms = [
        ("Mycobacterium tuberculosis H37Rv", "organism_id:83332 AND reviewed:true"),
        ("Plasmodium falciparum 3D7",        "organism_id:36329 AND reviewed:true"),
        ("Homo sapiens",                     "organism_id:9606  AND reviewed:true"),
        ("Vibrio cholerae",                  "organism_id:345073 AND reviewed:true"),
    ]

    for name, query in organisms:
        total = count_proteins(query)
        print(f"  {name:<40} {int(total):>8,} proteins")
        time.sleep(0.3)

    # ── SECTION 2: M. tuberculosis drug targets ──────────────────────
    print("\n[2/4] M. tuberculosis — Drug Target Proteins")
    print("-" * 65)

    query_mtb = (
        "organism_id:83332 AND reviewed:true "
        "AND keyword:KW-0046"   # KW-0046 = Antibiotic resistance
    )

    fields = "accession,id,gene_names,protein_name,length,cc_function,keyword"

    entries = fetch_proteins(query_mtb, fields, size=15)
    mtb_results = []

    print(f"  {'Accession':<12} {'Gene':<12} {'Length':>8}  {'Protein':<35}")
    print("  " + "-" * 70)

    for e in entries:
        row = parse_entry(e)
        mtb_results.append(row)
        print(f"  {row['accession']:<12} {row['gene']:<12} "
              f"{row['length_aa']:>8,}  {row['protein'][:33]:<35}")

    # ── SECTION 3: P. falciparum resistance proteins ─────────────────
    print("\n[3/4] P. falciparum — Reviewed Resistance Proteins")
    print("-" * 65)

    query_pf = (
        "organism_id:36329 AND reviewed:true "
        "AND keyword:KW-0046"
    )

    entries_pf = fetch_proteins(query_pf, fields, size=10)
    pf_results = []

    print(f"  {'Accession':<12} {'Gene':<12} {'Length':>8}  {'Protein':<35}")
    print("  " + "-" * 70)

    for e in entries_pf:
        row = parse_entry(e)
        pf_results.append(row)
        print(f"  {row['accession']:<12} {row['gene']:<12} "
              f"{row['length_aa']:>8,}  {row['protein'][:33]:<35}")

    # ── SECTION 4: Fetch your 5 resistance genes from UniProt ────────
    print("\n[4/4] Fetching Day 5 resistance genes from UniProt")
    print("-" * 65)

    # UniProt accessions for the 5 P. falciparum resistance proteins
    target_accessions = {
        "kelch13": "Q8IHN3",  # PfKelch13
        "crt":     "Q8IBZ9",  # PfCRT
        "mdr1":    "Q7K6A5",  # PfMDR1
        "dhfr":    "P13917",  # PfDHFR-TS
        "dhps":    "Q8I2F8",  # PfDHPS
    }

    detail_fields = "accession,id,gene_names,protein_name,length,cc_function,cc_disease,keyword,ft_variant"

    for gene, acc in target_accessions.items():
        url = f"https://rest.uniprot.org/uniprotkb/{acc}"
        r   = requests.get(url, params={"format": "json", "fields": detail_fields})

        if r.status_code != 200:
            print(f"  ❌ {gene} ({acc}) — not found")
            continue

        entry = r.json()
        row   = parse_entry(entry)

        print(f"\n  Gene      : {gene.upper()} ({acc})")
        print(f"  Entry     : {row['entry_name']}")
        print(f"  Protein   : {row['protein']}")
        print(f"  Length    : {row['length_aa']} aa")
        print(f"  Keywords  : {row['keywords']}")
        if row["function"]:
            print(f"  Function  : {row['function'][:100]}...")

        time.sleep(0.3)

    # ── Export CSVs ──────────────────────────────────────────────────
    print("\n\nExporting results...")

    if mtb_results:
        with open("results/day6_mtb_drug_targets.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=mtb_results[0].keys())
            writer.writeheader()
            writer.writerows(mtb_results)
        print("  Saved: results/day6_mtb_drug_targets.csv")

    if pf_results:
        with open("results/day6_pf_resistance_proteins.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=pf_results[0].keys())
            writer.writeheader()
            writer.writerows(pf_results)
        print("  Saved: results/day6_pf_resistance_proteins.csv")

    print("\n✅ Day 6 complete!")
    print("=" * 65)


if __name__ == "__main__":
    main()
