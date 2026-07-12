#!/usr/bin/env python3
"""
run_examples.py - simple runner to execute selected example scripts in this repo.

Usage:
  python run_examples.py --list
  python run_examples.py --days 4 5 6
  python run_examples.py --all

This script runs the scripts in the `scripts/` directory and streams output to stdout.
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = {
    4: "scripts/day4_parse_genbank.py",
    5: "scripts/day5_fetch_genes.py",
    6: "scripts/day6_mtb_deep.py",
    7: "scripts/day7_parse_pdb.py",
    8: "scripts/day8_ensembl.py",
}


def run_script(path: Path) -> int:
    print(f"\n=== Running: {path} ===\n")
    if not path.exists():
        print(f"ERROR: script not found: {path}")
        return 2
    # Use the same Python interpreter that's running this runner
    proc = subprocess.run([sys.executable, str(path)])
    return proc.returncode


def main():
    parser = argparse.ArgumentParser(description="Run training example scripts")
    parser.add_argument("--list", action="store_true", help="List available example scripts")
    parser.add_argument("--all", action="store_true", help="Run all example scripts (4-8)")
    parser.add_argument("--days", nargs="*", type=int, help="Which day(s) to run (e.g. 4 6)")
    args = parser.parse_args()

    if args.list:
        for d, p in SCRIPTS.items():
            print(f"Day {d}: {p}")
        return

    to_run = []
    if args.all:
        to_run = sorted(SCRIPTS.keys())
    elif args.days:
        to_run = [d for d in args.days if d in SCRIPTS]
    else:
        parser.print_help()
        return

    failed = []
    for d in to_run:
        path = Path(SCRIPTS[d])
        rc = run_script(path)
        if rc != 0:
            print(f"Script returned non-zero exit code: {rc}")
            failed.append((d, rc))

    if failed:
        print("\nOne or more scripts failed:")
        for d, rc in failed:
            print(f"  Day {d}: exit {rc}")
        sys.exit(1)
    else:
        print("\nAll requested scripts completed successfully.")


if __name__ == "__main__":
    main()
