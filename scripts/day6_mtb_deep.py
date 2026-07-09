# scripts/day6_mtb_deep.py
# Author: Boris Djagou
# Date: July 8, 2026
# Deep annotation of top M. tuberculosis drug targets from UniProt

import requests
import csv
import time

ENTRY = "https://rest.uniprot.org/uniprotkb"

# Top 5 TB drug targets — verified UniProt accessions
MTB_TARGETS = [
    {"gene": "inhA",  "accession": "P9WGR1",
     "drug": "Isoniazid, Ethionamide",
     "note": "Most important TB drug target — enoyl-ACP reductase"},
    {"gene": "katG",  "accession": "P9WKD3",
     "drug": "Isoniazid (activator)",
     "note": "Activates isoniazid — mutations cause isoniazid resistance"},
    {"gene": "gyrA",  "accession": "P9WG47",
     "drug": "Fluoroquinolones (ciprofloxacin, levofloxacin)",
     "note": "DNA gyrase subunit — key target in MDR-TB treatment"},
    {"gene": "pncA",  "accession": "I6XD65",
     "drug": "Pyrazinamide",
     "note": "Converts pyrazinamide to active pyrazinoic acid"},
    {"gene": "rpoB",  "accession": "P0A608",
     "drug": "Rifampicin",
     "note": "RNA polymerase beta — mutations cause rifampicin resistance"},
]


def fetch_full_entry(accession):
    """Fetch complete UniProt entry as JSON."""
    r = requests.get(f"{ENTRY}/{accession}", params={"format": "json"})
    if r.status_code == 200:
        return r.json()
    return None


def extract_variants(entry):
    """Extract natural variants (resistance mutations) from UniProt."""
    variants = []
    for feature in entry.get("features", []):
        if feature.get("type") == "Natural variant":
            pos   = feature.get("location", {})
            start = pos.get("start", {}).get("value", "?")
            orig  = feature.get("alternativeSequence", {})
            wt    = orig.get("originalSequence", "?")
            mut   = orig.get("alternativeSequences", ["?"])[0]
            desc  = feature.get("description", "")
            variants.append({
                "position": start,
                "wt":       wt,
                "mut":      mut,
                "effect":   desc[:80],
            })
    return variants


def extract_active_sites(entry):
    """Extract active site residues."""
    sites = []
    for feature in entry.get("features", []):
        if feature.get("type") in ["Active site", "Binding site"]:
            pos  = feature.get("location", {})
            start= pos.get("start", {}).get("value", "?")
            desc = feature.get("description", "")
            sites.append(f"pos {start}: {desc[:40]}")
    return sites[:5]


def main():
    print("\n🦠 Day 6 Deep Dive — M. tuberculosis Drug Targets (UniProt)")
    print("=" * 68)

    all_results = []

    for target in MTB_TARGETS:
        print(f"\n{'='*68}")
        print(f"  Gene      : {target['gene'].upper()}  ({target['accession']})")
        print(f"  Drug      : {target['drug']}")
        print(f"  Note      : {target['note']}")

        entry = fetch_full_entry(target["accession"])
        if not entry:
            print(f"  ❌ Could not fetch {target['accession']}")
            continue

        # Basic info
        acc      = entry.get("primaryAccession", "")
        length   = entry.get("sequence", {}).get("length", 0)
        keywords = [k.get("name","") for k in entry.get("keywords", [])]

        # Function
        function = ""
        for c in entry.get("comments", []):
            if c.get("commentType") == "FUNCTION":
                texts = c.get("texts", [])
                if texts:
                    function = texts[0].get("value", "")
                break

        # Disease / resistance
        disease = ""
        for c in entry.get("comments", []):
            if c.get("commentType") in ["DISEASE", "MISCELLANEOUS"]:
                texts = c.get("texts", [])
                if texts:
                    disease = texts[0].get("value", "")[:150]
                break

        # Subcellular location
        location = ""
        for c in entry.get("comments", []):
            if c.get("commentType") == "SUBCELLULAR LOCATION":
                locs = c.get("subcellularLocations", [])
                if locs:
                    loc_names = [
                        l.get("location", {}).get("value", "")
                        for l in locs
                    ]
                    location = " | ".join(loc_names[:3])
                break

        # Variants and active sites
        variants     = extract_variants(entry)
        active_sites = extract_active_sites(entry)

        print(f"  Length    : {length} aa")
        print(f"  Location  : {location or 'N/A'}")
        print(f"  Keywords  : {', '.join(keywords[:6])}")
        print(f"\n  Function  : {function[:200]}...")

        if active_sites:
            print(f"\n  Active sites ({len(active_sites)}):")
            for s in active_sites:
                print(f"    • {s}")

        if variants:
            print(f"\n  Resistance variants ({len(variants)} total):")
            for v in variants[:5]:
                print(f"    • pos {v['position']}: {v['wt']} → {v['mut']}  "
                      f"({v['effect'][:60]})")
            if len(variants) > 5:
                print(f"    ... and {len(variants)-5} more")

        # Fetch FASTA
        r_fasta = requests.get(
            f"{ENTRY}/{target['accession']}",
            params={"format": "fasta"}
        )
        if r_fasta.status_code == 200:
            path = f"results/day6_{target['gene']}_protein.fasta"
            with open(path, "w") as f:
                f.write(r_fasta.text)
            print(f"\n  FASTA saved: {path}")

        all_results.append({
            "gene":        target["gene"],
            "accession":   acc,
            "drug":        target["drug"],
            "length_aa":   length,
            "location":    location,
            "function":    function[:200],
            "variants":    len(variants),
            "note":        target["note"],
        })

        time.sleep(0.4)

    # Summary table
    print(f"\n\n{'='*68}")
    print("SUMMARY — M. tuberculosis Top 5 Drug Targets")
    print(f"{'='*68}")
    print(f"  {'Gene':<8} {'Accession':<12} {'Drug':<30} "
          f"{'Length':>8} {'Variants':>9}")
    print("  " + "-" * 72)
    for r in all_results:
        print(f"  {r['gene']:<8} {r['accession']:<12} "
              f"{r['drug']:<30} {r['length_aa']:>8,} "
              f"{r['variants']:>9}")

    # Export CSV
    if all_results:
        csv_path = "results/day6_mtb_top5_targets.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n  CSV saved: {csv_path}")

    print("\n✅ Day 6 deep dive complete!")
    print("=" * 68)


if __name__ == "__main__":
    main()
