#!/usr/bin/env python3
"""
generate_inc.py - Converts Markdown files in para-misales/ into Typst .inc files.

Usage:
    python3 generate_inc.py 2026-09-27
    python3 generate_inc.py 20260927

All shared logic lives in misal.py; this file is the CLI entry point.
"""

import argparse
import sys

from misal import generate_inc_file


def main():
    parser = argparse.ArgumentParser(description="Generate Typst .inc file from Markdown liturgy sources.")
    parser.add_argument("date", help="Date in YYYY-MM-DD or YYYYMMDD format (e.g. 2026-09-27)")
    args = parser.parse_args()

    try:
        generate_inc_file(args.date)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
