# scripts/day6_fix.py
# Author: Boris Djagou
# Date: July 8, 2026
# Fix: correct UniProt accessions + P. falciparum keyword query

import requests
import time

BASE   = "https://rest.uniprot.org/uniprotkb/search"
ENTRY  = "https://rest.uniprot.org/uniprotkb"


def parse_entry(entry):
    acc      = entry.get("primaryAccession", "")
    name     = entry.get("uniProtkbId",      "")
    prot     = entry.get("proteinDescription", {})
    rec      = prot.get("recommendedName", {})
    fullname = rec.get("fullName", {}).get("value", "unknown") if rec \
               else "unknown"
    genes    = entry.get("genes", [{}])
    gene     = genes[0].get("geneName", {}).get("value", "unknown") \
               if genes else "unknown"
    seq      = entry.get("sequence", {})
    length   = seq.get("length", 0)
    comments = entry.get("comments", [])
    function = ""
    for c in comments:
        if c.get("commentType") == "FUNCTION":
            texts = c.get("texts", [])
            if texts:
                function = texts[0].get("value", "")[:150]
            break
    keywords = [k.get("name","") for k in entry.get("keywords", [])][:5]
    return {
        "accession": acc, "entry_name": name,
        "gene": gene,    "protein":    fullname,
        "length_aa": length, "function": function,
        "keywords": " | ".join(keywords),
    }


def main():
    print("\n🔧 Day 6 Fix — Correct UniProt Accessions for All 5 Genes")
    print("=" * 65)

    # ── FIX 1: P. falciparum resistance proteins ─────────────────────
    # Use search by gene name + organism — more reliable than hardcoded accessions
    print("\n[1/3] Searching P. falciparum resistance proteins by gene name")
    print("-" * 65)

    pf_genes = [
        {"gene": "kelch13", "search": "gene:K13 AND organism_id:36329",
         "expected_aa": 726},
        {"gene": "crt",     "search": "gene:CRT AND organism_id:36329 AND reviewed:true",
         "expected_aa": 424},
        {"gene": "mdr1",    "search": "gene:MDR1 AND organism_id:36329 AND reviewed:true",
         "expected_aa": 1419},
        {"gene": "dhfr",    "search": "gene:DHFR AND organism_id:36329 AND reviewed:true",
         "expected_aa": 608},
        {"gene": "dhps",    "search": "gene:DHPS AND organism_id:36329",
         "expected_aa": 706},
    ]

    pf_found = []
    for g in pf_genes:
        r = requests.get(BASE, params={
            "query": g["search"], "format": "json", "size": 5
        })
        results = r.json().get("results", [])

        print(f"\n  [{g['gene'].upper()}] — expected {g['expected_aa']} aa")
        found = False
        for entry in results:
            row = parse_entry(entry)
            diff = abs(row["length_aa"] - g["expected_aa"])
            status = "✅" if diff <= 60 else "⚠"
            print(f"    {status} {row['accession']:<12} {row['entry_name']:<20} "
                  f"{row['length_aa']:>5} aa  {row['protein'][:35]}")
            if diff <= 60 and not found:
                pf_found.append({**row, "target_gene": g["gene"]})
                found = True
        if not found:
            print(f"    ❌ No match found")
        time.sleep(0.3)

    # ── FIX 2: P. falciparum keyword query ───────────────────────────
    print("\n\n[2/3] P. falciparum proteins — using correct keywords")
    print("-" * 65)

    # Use 'Malaria' keyword (KW-0478) instead of antibiotic resistance
    pf_queries = [
        ("Reviewed PF proteins — any",
         "organism_id:36329 AND reviewed:true"),
        ("PF proteins — drug resistance keyword",
         "organism_id:36329 AND keyword:KW-0138"),   # KW-0138 = Drug resistance
        ("PF proteins — antimalarial",
         "organism_id:36329 AND keyword:KW-0478"),   # KW-0478 = Malaria
    ]

    for label, query in pf_queries:
        r = requests.get(BASE, params={
            "query": query, "format": "json", "size": 1
        })
        total = r.headers.get("X-Total-Results", "0")
        print(f"  {label:<45} {int(total):>6,} proteins")
        time.sleep(0.3)

    # Fetch PF drug resistance proteins with correct keyword
    print("\n  P. falciparum — Drug resistance proteins (KW-0138):")
    r = requests.get(BASE, params={
        "query":  "organism_id:36329 AND keyword:KW-0138",
        "format": "json",
        "size":   10,
        "fields": "accession,id,gene_names,protein_name,length,keyword"
    })
    pf_dr = r.json().get("results", [])
    print(f"  {'Accession':<12} {'Gene':<12} {'Length':>8}  {'Protein':<35}")
    print("  " + "-" * 70)
    for e in pf_dr:
        row = parse_entry(e)
        print(f"  {row['accession']:<12} {row['gene']:<12} "
              f"{row['length_aa']:>8,}  {row['protein'][:33]}")

    # ── FIX 3: Summary of correct accessions ─────────────────────────
    print("\n\n[3/3] Summary — Correct UniProt entries for 5 resistance genes")
    print("-" * 65)
    print(f"  {'Gene':<10} {'Accession':<14} {'Entry':<22} "
          f"{'Length':>8}  {'Protein':<30}")
    print("  " + "-" * 88)
    for row in pf_found:
        print(f"  {row['target_gene']:<10} {row['accession']:<14} "
              f"{row['entry_name']:<22} {row['length_aa']:>8,}  "
              f"{row['protein'][:28]}")

    print("\n✅ Fix complete!")
    print("=" * 65)


if __name__ == "__main__":
    main()
