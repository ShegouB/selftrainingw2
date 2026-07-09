# scripts/day8_ensembl.py
# Author: Boris Djagou
# Date: July 10, 2026
# Topic: Ensembl REST API — gene coordinates + orthologs

import requests
import csv
import time
import json

ENSEMBL    = "https://rest.ensembl.org"
ENSEMBL_EG = "https://rest.ensemblgenomes.org"
HEADERS    = {"Content-Type": "application/json"}


def get_gene_info(gene_id, server=ENSEMBL_EG):
    """Get gene information by Ensembl/EnsemblGenomes ID."""
    r = requests.get(f"{server}/lookup/id/{gene_id}",
                     headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    return {}


def get_gene_sequence(gene_id, server=ENSEMBL_EG, seq_type="genomic"):
    """Fetch gene sequence."""
    r = requests.get(
        f"{server}/sequence/id/{gene_id}",
        headers=HEADERS,
        params={"type": seq_type}
    )
    if r.status_code == 200:
        return r.json().get("seq", "")
    return ""


def get_orthologs(gene_id, target_species, server=ENSEMBL_EG):
    """Get orthologs in a target species."""
    r = requests.get(
        f"{server}/homology/id/{gene_id}",
        headers=HEADERS,
        params={
            "target_species": target_species,
            "type":           "orthologues",
            "format":         "condensed",
        }
    )
    if r.status_code == 200:
        data = r.json()
        homologies = data.get("data", [{}])[0].get("homologies", [])
        return homologies
    return []


def get_xrefs(gene_id, server=ENSEMBL_EG):
    """Get cross-references to external databases."""
    r = requests.get(f"{server}/xrefs/id/{gene_id}",
                     headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    return []


def main():
    print("\n🧬 Day 8 — Ensembl REST API")
    print("=" * 65)

    # ── SECTION 1: P. falciparum gene coordinates ────────────────────
    print("\n[1/4] P. falciparum Resistance Genes — Coordinates & Info")
    print("-" * 65)

    pf_genes = [
        {"id": "PF3D7_1343700", "name": "kelch13",
         "role": "Artemisinin resistance"},
        {"id": "PF3D7_0709000", "name": "crt",
         "role": "Chloroquine resistance"},
        {"id": "PF3D7_0523000", "name": "mdr1",
         "role": "Multidrug resistance"},
    ]

    gene_info_results = []

    for gene in pf_genes:
        print(f"\n  [{gene['name'].upper()}] {gene['role']}")
        info = get_gene_info(gene["id"])

        if not info:
            print(f"  ❌ Not found in EnsemblGenomes")
            continue

        chrom  = info.get("seq_region_name", "?")
        start  = info.get("start", 0)
        end    = info.get("end",   0)
        strand = "+" if info.get("strand", 0) == 1 else "-"
        length = end - start
        desc   = info.get("description", "N/A")

        print(f"  Ensembl ID   : {info.get('id', '?')}")
        print(f"  Chromosome   : {chrom}")
        print(f"  Position     : {start:,} → {end:,} ({strand} strand)")
        print(f"  Gene length  : {length:,} bp")
        print(f"  Description  : {desc[:70]}")

        gene_info_results.append({
            "gene_name":   gene["name"],
            "ensembl_id":  gene["id"],
            "role":        gene["role"],
            "chromosome":  chrom,
            "start":       start,
            "end":         end,
            "strand":      strand,
            "length_bp":   length,
        })

        time.sleep(0.4)

    # ── SECTION 2: Human orthologs of 3 PF genes ─────────────────────
    print("\n\n[2/4] Human Orthologs of P. falciparum Resistance Genes")
    print("-" * 65)

    ortholog_results = []

    for gene in pf_genes:
        print(f"\n  [{gene['name'].upper()}] — searching human orthologs...")

        orthologs = get_orthologs(
            gene["id"],
            target_species="homo_sapiens"
        )

        if not orthologs:
            print(f"  No human orthologs found (expected for parasite-specific genes)")

            # Try broader search — any vertebrate ortholog
            orthologs_vert = get_orthologs(
                gene["id"],
                target_species="mus_musculus"
            )
            if orthologs_vert:
                print(f"  Mouse orthologs found: {len(orthologs_vert)}")
                for o in orthologs_vert[:2]:
                    tid  = o.get("target", {}).get("id", "?")
                    tsym = o.get("target", {}).get("gene_id", tid)
                    otype= o.get("type", "?")
                    pid  = o.get("target", {}).get("perc_id", "?")
                    print(f"    {tsym} ({tid}) — {otype} — {pid}% identity")
        else:
            print(f"  Human orthologs found: {len(orthologs)}")
            for o in orthologs:
                tid    = o.get("target", {}).get("id", "?")
                tsym   = o.get("target", {}).get("gene_id", tid)
                otype  = o.get("type", "?")
                pid    = o.get("target", {}).get("perc_id", "?")
                print(f"    {tsym:<20} ({tid:<20}) {otype:<25} {pid}% id")
                ortholog_results.append({
                    "pf_gene":         gene["name"],
                    "pf_id":           gene["id"],
                    "human_gene":      tsym,
                    "human_ensembl_id":tid,
                    "type":            otype,
                    "percent_identity":pid,
                })

        time.sleep(0.5)

    # ── SECTION 3: Human gene lookup + coordinates ────────────────────
    print("\n\n[3/4] Key Human Genes Related to Malaria Host Response")
    print("-" * 65)

    human_genes = [
        ("G6PD",  "Glucose-6-phosphate dehydrogenase — G6PD deficiency protects vs malaria"),
        ("DARC",  "Duffy antigen receptor — P. vivax invasion receptor"),
        ("HBB",   "Hemoglobin beta — sickle cell trait protects vs malaria"),
        ("CR1",   "Complement receptor 1 — P. falciparum rosetting receptor"),
        ("GYPA",  "Glycophorin A — invasion ligand for EBA-175"),
    ]

    human_gene_results = []

    for symbol, desc in human_genes:
        r = requests.get(
            f"{ENSEMBL}/lookup/symbol/homo_sapiens/{symbol}",
            headers=HEADERS
        )
        if r.status_code != 200:
            print(f"  ❌ {symbol} not found")
            continue

        g      = r.json()
        chrom  = g.get("seq_region_name", "?")
        start  = g.get("start", 0)
        end    = g.get("end",   0)
        strand = "+" if g.get("strand", 1) == 1 else "-"

        print(f"  {symbol:<6} chr{chrom}:{start:,}-{end:,} ({strand}) | {desc[:55]}")

        human_gene_results.append({
            "symbol":    symbol,
            "ensembl_id":g.get("id", ""),
            "chromosome":chrom,
            "start":     start,
            "end":       end,
            "strand":    strand,
            "note":      desc,
        })
        time.sleep(0.3)

    # ── SECTION 4: Cross-references for kelch13 ──────────────────────
    print("\n\n[4/4] Cross-References for kelch13 (PF3D7_1343700)")
    print("-" * 65)

    xrefs = get_xrefs("PF3D7_1343700")
    db_counts = {}
    for x in xrefs:
        db = x.get("dbname", "unknown")
        db_counts[db] = db_counts.get(db, 0) + 1

    print(f"  Total cross-references: {len(xrefs)}")
    print(f"  Databases referenced ({len(db_counts)}):")
    for db, count in sorted(db_counts.items()):
        print(f"    {db:<30} {count:>3} entries")

    # ── Export CSVs ───────────────────────────────────────────────────
    print("\n\nExporting results...")

    if gene_info_results:
        with open("results/day8_pf_gene_coordinates.csv", "w",
                  newline="") as f:
            writer = csv.DictWriter(f,
                                    fieldnames=gene_info_results[0].keys())
            writer.writeheader()
            writer.writerows(gene_info_results)
        print("  Saved: results/day8_pf_gene_coordinates.csv")

    if ortholog_results:
        with open("results/day8_orthologs.csv", "w", newline="") as f:
            writer = csv.DictWriter(f,
                                    fieldnames=ortholog_results[0].keys())
            writer.writeheader()
            writer.writerows(ortholog_results)
        print("  Saved: results/day8_orthologs.csv")

    if human_gene_results:
        with open("results/day8_human_malaria_genes.csv", "w",
                  newline="") as f:
            writer = csv.DictWriter(f,
                                    fieldnames=human_gene_results[0].keys())
            writer.writeheader()
            writer.writerows(human_gene_results)
        print("  Saved: results/day8_human_malaria_genes.csv")

    print("\n✅ Day 8 complete!")
    print("=" * 65)


if __name__ == "__main__":
    main()
