#!/usr/bin/env python3
"""
haz-misal.py - Generates .inc files and compiles the missals: the two printable
PDFs and the web edition (HTML) of the sjb sheet.

Usage:
    python3 haz-misal.py 2026-09-27
    python3 haz-misal.py 2026-09-27 --template sjb
    python3 haz-misal.py 2026-09-27 --template web-sjb
    python3 haz-misal.py --all          # every date, every template
"""

import argparse
import csv
import sys
import tempfile
from pathlib import Path

from misal import generate_inc_file, normalize_date, compilar_typst, typst_bool, BASE_DIR, CALENDARIO_PATH, SJB_TYP_CONTENT, AJUSTES_MISAL, TEMPLATES

def compile_template(template_name: str, inc_file_name: str, date_compact: str):
    output_pattern, content_template, export_format = TEMPLATES[template_name]
    output_name = output_pattern.format(date_compact=date_compact)
    output_path = BASE_DIR / output_name

    # portada, separador, mensual y ajustes sólo los usa el envoltorio de sjb,
    # que es el que reutiliza el misal mensual; las otras plantillas ignoran los
    # argumentos que no aparecen en su texto. El misal diario va siempre con
    # portada, sin separador y sin portada de mensual (las dos cosas son del
    # cuaderno del mes), y con los ajustes de página incluidos una sola vez, al
    # principio: el mensual los incluye él mismo en el maestro, porque cada
    # `set page` que entra en vigor abre página nueva.
    typ_code = content_template.format(
        inc_file=inc_file_name,
        portada=typst_bool(True),
        separador=typst_bool(False),
        mensual=typst_bool(False),
        ajustes=AJUSTES_MISAL,
    )

    with tempfile.NamedTemporaryFile("w", dir=BASE_DIR, suffix=".typ", delete=False, encoding="utf-8") as tmp_file:
        tmp_file.write(typ_code)
        tmp_path = Path(tmp_file.name)

    try:
        return compilar_typst(tmp_path, output_path, export_format)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

def build_for_date(date_str: str, template: str = "all") -> bool:
    try:
        formatted_date, date_compact = normalize_date(date_str)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

    inc_path = generate_inc_file(date_str)
    # "all" is everything the site publishes: the two printable missals plus the
    # web edition. --template web-sjb still builds only the HTML.
    templates_to_compile = ["sjb", "cjsjb", "web-sjb"] if template == "all" else [template]
    success = True
    for t_name in templates_to_compile:
        if not compile_template(t_name, inc_path.name, date_compact):
            success = False
    return success

def get_all_dates_from_calendar() -> list[str]:
    dates = []
    if CALENDARIO_PATH.exists():
        with open(CALENDARIO_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                d = row.get("fecha", "").strip()
                if d:
                    dates.append(d)
    return dates

def main():
    parser = argparse.ArgumentParser(description="Build missals for a given date or all dates in calendar.")
    parser.add_argument("date", nargs="?", help="Date in YYYY-MM-DD or YYYYMMDD format (e.g. 2026-09-27)")
    parser.add_argument("--all", action="store_true", help="Build missals for all dates in calendario.csv")
    parser.add_argument(
        "--template",
        choices=["sjb", "cjsjb", "web-sjb", "all"],
        default="all",
        help=(
            "Template to compile: sjb or cjsjb (PDF), web-sjb (HTML), "
            "all = every template (default: all)"
        ),
    )
    args = parser.parse_args()

    if args.all:
        dates = get_all_dates_from_calendar()
        if not dates:
            print("No dates found in calendario.csv", file=sys.stderr)
            sys.exit(1)
        success = True
        for d in dates:
            if not build_for_date(d, args.template):
                success = False
        if not success:
            sys.exit(1)
    elif args.date:
        if not build_for_date(args.date, args.template):
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
