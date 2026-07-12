# Makefile for selftrainingw2

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: install run-day4 run-day5 run-day6 run-day7 run-day8 run-all clean

install:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run-day4:
	$(PY) scripts/day4_parse_genbank.py

run-day5:
	$(PY) scripts/day5_fetch_genes.py

run-day6:
	$(PY) scripts/day6_mtb_deep.py

run-day7:
	$(PY) scripts/day7_parse_pdb.py

run-day8:
	$(PY) scripts/day8_ensembl.py

run-all: run-day4 run-day5 run-day6 run-day7 run-day8

clean:
	rm -rf $(VENV)
	rm -f results/*.csv results/*.fasta results/*.txt
