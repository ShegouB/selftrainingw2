# scripts/day5_pubmed.py
# Author: Boris Djagou
# Date: July 7, 2026
# Topic: Search PubMed for recent papers on artemisinin resistance

from Bio import Entrez
import time

Entrez.email = "djagouboris@gmail.com"

def search_pubmed(query, max_results=5):
    """Search PubMed and return article details."""
    handle = Entrez.esearch(db="pubmed", term=query,
                            retmax=max_results, sort="relevance")
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]


def fetch_abstracts(id_list):
    """Fetch titles and abstracts for a list of PubMed IDs."""
    ids = ",".join(id_list)
    handle = Entrez.efetch(db="pubmed", id=ids,
                           rettype="abstract", retmode="text")
    data = handle.read()
    handle.close()
    return data


def main():
    queries = [
        "artemisinin resistance kelch13 West Africa",
        "Plasmodium falciparum Benin genomics",
        "malaria drug resistance West Africa 2024",
    ]

    print("\n PubMed Search — Malaria Resistance Literature")
    print("=" * 55)

    all_output = []

    for query in queries:
        print(f"\nQuery: '{query}'")
        ids = search_pubmed(query, max_results=3)
        print(f"Found {len(ids)} articles: {ids}")

        if ids:
            abstracts = fetch_abstracts(ids)
            all_output.append(f"\n{'='*55}")
            all_output.append(f"Query: {query}")
            all_output.append(f"PubMed IDs: {ids}")
            all_output.append(abstracts)

        time.sleep(0.5)

    # Save to file
    output_path = "results/day5_pubmed_results.txt"
    with open(output_path, "w") as f:
        f.write("\n".join(all_output))
    print(f"\nAbstracts saved: {output_path}")
    print("=" * 55)


if __name__ == "__main__":
    main()
