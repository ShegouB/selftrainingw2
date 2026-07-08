# scripts/day6_fix_katg_rpob.py
# Author: Boris Djagou
# Date: July 8, 2026

import requests
import time

ENTRY = "https://rest.uniprot.org/uniprotkb"
BASE  = "https://rest.uniprot.org/uniprotkb/search"


def search_protein(query, size=5):
    r = requests.get(BASE, params={
        "query": query, "format": "json", "size": size,
        "fields": "accession,id,gene_names,protein_name,length"
    })
    return r.json().get("results", [])


def fetch_fasta(accession, gene_name):
    r = requests.get(f"{ENTRY}/{accession}", params={"format": "fasta"})
    if r.status_code == 200 and len(r.text) > 50:
        path = f"results/day6_{gene_name}_protein.fasta"
        with open(path, "w") as f:
            f.write(r.text)
        return path
    return None


def main():
    print("\n🔧 Fixing katG and rpoB accessions")
    print("=" * 60)

    fixes = [
        {
            "gene":        "katG",
            "query":       "gene:katG AND organism_id:83332 AND reviewed:true",
            "expected_aa": 740,
            "drug":        "Isoniazid activator",
        },
        {
            "gene":        "rpoB",
            "query":       "gene:rpoB AND organism_id:83332 AND reviewed:true",
            "expected_aa": 1173,
            "drug":        "Rifampicin — most important resistance gene",
        },
    ]

    for fix in fixes:
        print(f"\n[{fix['gene'].upper()}] — {fix['drug']}")
        print(f"  Expected: {fix['expected_aa']} aa")

        results = search_protein(fix["query"])

        print(f"  {'Accession':<14} {'Entry':<22} {'Length':>8}  {'Protein':<35}")
        print("  " + "-" * 82)

        best = None
        for e in results:
            acc    = e.get("primaryAccession", "")
            name   = e.get("uniProtkbId", "")
            length = e.get("sequence", {}).get("length", 0)
            prot   = e.get("proteinDescription", {})
            rec    = prot.get("recommendedName", {})
            pname  = rec.get("fullName", {}).get("value", "?") if rec else "?"
            diff   = abs(length - fix["expected_aa"])
            status = "✅" if diff <= 100 else "⚠ "
            print(f"  {status} {acc:<14} {name:<22} {length:>8,}  {pname[:33]}")
            if diff <= 100 and best is None:
                best = (acc, name, length, pname)

        if best:
            acc, name, length, pname = best
            print(f"\n  → Best match: {acc} ({name}) — {length} aa")
            fasta_path = fetch_fasta(acc, fix["gene"])
            if fasta_path:
                print(f"  → FASTA saved: {fasta_path}")
        else:
            print(f"  ❌ No match found within ±100 aa of expected")

        time.sleep(0.4)

    # Now fetch rpoB resistance variants specifically
    print("\n\n[rpoB RESISTANCE VARIANTS]")
    print("-" * 60)
    print("  rpoB encodes RNA polymerase beta subunit.")
    print("  Rifampicin resistance mutations concentrate in")
    print("  the 81bp RRDR (Rifampicin Resistance Determining Region)")
    print("  codons 507–533 in M. tuberculosis numbering.")
    print()

    # Fetch full rpoB entry for variants
    results = search_protein(
        "gene:rpoB AND organism_id:83332 AND reviewed:true", size=1
    )
    if results:
        acc = results[0].get("primaryAccession", "")
        r   = requests.get(f"{ENTRY}/{acc}", params={"format": "json"})
        if r.status_code == 200:
            entry    = r.json()
            length   = entry.get("sequence", {}).get("length", 0)
            features = entry.get("features", [])
            variants = [f for f in features if f.get("type") == "Natural variant"]

            print(f"  Accession: {acc}  |  Length: {length} aa")
            print(f"  Total natural variants: {len(variants)}")

            # Show resistance variants
            resist_vars = [
                v for v in variants
                if "resistance" in v.get("description", "").lower()
                or "rifamp" in v.get("description", "").lower()
            ]
            print(f"  Resistance-related variants: {len(resist_vars)}")

            if resist_vars:
                print(f"\n  {'Position':>10} {'WT':>5} {'Mut':>5}  Effect")
                print("  " + "-" * 65)
                for v in resist_vars[:15]:
                    pos  = v.get("location", {}).get("start", {}).get("value", "?")
                    orig = v.get("alternativeSequence", {})
                    wt   = orig.get("originalSequence", "?")
                    mut  = orig.get("alternativeSequences", ["?"])[0]
                    desc = v.get("description", "")[:55]
                    print(f"  {str(pos):>10} {wt:>5} {mut:>5}  {desc}")
                if len(resist_vars) > 15:
                    print(f"  ... and {len(resist_vars)-15} more resistance variants")

    print("\n✅ Fix complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
