# selftrainingw2

By Boris Djagou (ShegouB)

A small collection of bioinformatics training scripts and example data used for hands-on self-training exercises. The repository contains worked examples (Days 4–8) that demonstrate using Biopython, NCBI Entrez, UniProt/Ensembl REST APIs, and PDB parsing to inspect genomic, protein, and structural data for Plasmodium falciparum and Mycobacterium tuberculosis targets.

Key goals
- Provide short, runnable Python scripts that show common bioinformatics tasks (GenBank parsing, fetching sequences, querying UniProt/Ensembl, parsing PDBs).
- Save intermediate results (FASTA files, CSV summaries) under `results/` so outputs are reproducible and inspectable.
- Keep data used for examples in `data/` (genome, GenBank, PDB files).

Stack
- Language: Python (3.8+ recommended)
- Notable libraries: Biopython, requests

Repository structure

```text
data/
  pfalciparum_3D7_genome.fna   # raw genome FASTA (large)
  pfalciparum_chr1.gbk         # GenBank file used for parsing examples
  pdb/                         # PDB files used by day7 scripts (download separately)
results/
  *.fasta, *.csv, *.txt        # outputs produced by the scripts
scripts/
  day4_parse_genbank.py        # parse GenBank, extract CDS annotations
  day4_biopython.py            # (other Biopython examples)
  day5_*                       # Entrez, PubMed, fetch resistance proteins
  day6_*                       # UniProt deep annotations for M. tuberculosis targets
  day7_*                       # Parse PDB structures (chains, ligands, B-factors)
  day8_ensembl.py              # Ensembl REST API examples (coordinates, orthologs)

```

How to run (short path)

1. Clone the repo:

```bash
git clone https://github.com/ShegouB/selftrainingw2.git
cd selftrainingw2
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install biopython requests
```

(If you prefer, install any other libraries referenced in scripts; there is no requirements.txt in this repo.)

3. Run an example script. Examples below assume you have the required data files in `data/` and write outputs to `results/`.

- Parse GenBank (day 4):

```bash
python scripts/day4_parse_genbank.py
```

- Fetch and save UniProt entries for TB drug targets (day 6):

```bash
python scripts/day6_mtb_deep.py
```

- Parse PDB structures (day 7):

```bash
# ensure PDB files (e.g. 1p44.pdb) are in data/pdb/
python scripts/day7_parse_pdb.py
```

Notes & requirements
- Biopython is required for many scripts (SeqIO, Bio.PDB, Entrez, etc.).
- Several scripts call external services (NCBI Entrez, UniProt REST, Ensembl REST). These require an Internet connection and are subject to API rate limits.
- For NCBI Entrez usage, scripts set Entrez.email in `scripts/day5_fetch_genes.py`. Please set `Entrez.email` to your own email if you run Entrez queries frequently.
- Large data files: `data/pfalciparum_3D7_genome.fna` is large — keep it locally if you plan to re-run genome-scale examples.
- PDB files are not all included: place downloaded PDB files under `data/pdb/` (scripts look for both lowercase and uppercase PDB IDs).

Outputs
- Scripts write outputs to `results/` (FASTA, CSV, plain text). These were included as example outputs from the training exercises.

Missing items / suggestions
- Add a requirements.txt or pyproject.toml to pin dependencies.
- Add a LICENSE to make reuse terms clear (currently none is specified).
- Add small helper CLI or Makefile to standardize running examples.

Contributing
- Small fixes and documentation improvements are welcome. For code changes, please open a pull request and include a short description of the change and which script it affects.

Contact
- Repository owner: https://github.com/ShegouB
- Author in scripts: Boris Djagou (djagouboris@gmail.com)

Acknowledgements
- Examples use public databases and the Biopython project.
