#!/usr/bin/env python3
"""
haz-misal.py - Generates .inc files and compiles missal PDFs (and, opt-in, the
web edition of the sjb sheet as HTML).

Usage:
    python3 haz-misal.py 2026-09-27
    python3 haz-misal.py 2026-09-27 --template sjb
    python3 haz-misal.py 2026-09-27 --template web-sjb
    python3 haz-misal.py --all
"""

import argparse
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

from generate_inc import generate_inc_file, normalize_date

BASE_DIR = Path(__file__).parent.resolve()
CALENDARIO_PATH = BASE_DIR / "calendario.csv"
FONTS_DIR = BASE_DIR / "fonts"

CJSJB_TYP_CONTENT = """#import "template-cjsjb.typ": render-cjsjb
#import "common-defaults.typ": *
#import "{inc_file}": *

#render-cjsjb(
  tiempo: tiempo,
  domingo_num: domingo_num,
  fecha: fecha,
  frase: frase,
  canto_entrada: canto_entrada,
  canto_sennortenpiedad: canto_sennortenpiedad,
  canto_gloria: canto_gloria,
  canto_aleluya: canto_aleluya,
  canto_ofertorio: canto_ofertorio,
  canto_santo: canto_santo,
  canto_corderodedios: canto_corderodedios,
  canto_comunion: canto_comunion,
  canto_postcomunion: canto_postcomunion,
  canto_salida: canto_salida,
  oracion_colecta: oracion_colecta,
  lectura_primera_fuente: lectura_primera_fuente,
  lectura_primera: lectura_primera,
  salmo_fuente: salmo_fuente,
  salmo_partitura: salmo_partitura,
  salmo_aclamacion: salmo_aclamacion,
  salmo_estrofas: salmo_estrofas,
  lectura_segunda_fuente: lectura_segunda_fuente,
  lectura_segunda: lectura_segunda,
  aleluya_fuente: aleluya_fuente,
  aleluya_aclamacion: aleluya_aclamacion,
  evangelio_fuente: evangelio_fuente,
  evangelio: evangelio,
  oracion_delosfieles: oracion_delosfieles,
  oracion_ofrendas: oracion_ofrendas,
  oracion_comunion: oracion_comunion,
  monicion_entrada: monicion_entrada,
  monicion_ofrendas: monicion_ofrendas,
)
"""

SJB_TYP_CONTENT = """#import "template-sjb.typ": render-sjb
#import "common-defaults.typ": *
#import "{inc_file}": *

#render-sjb(
  tiempo: tiempo,
  domingo_num: domingo_num,
  fecha: fecha,
  frase: frase,
  oracion_colecta: oracion_colecta,
  lectura_primera_fuente: lectura_primera_fuente,
  lectura_primera: lectura_primera,
  salmo_fuente: salmo_fuente,
  salmo_partitura: salmo_partitura,
  salmo_aclamacion: salmo_aclamacion,
  salmo_estrofas: salmo_estrofas,
  lectura_segunda_fuente: lectura_segunda_fuente,
  lectura_segunda: lectura_segunda,
  aleluya_fuente: aleluya_fuente,
  aleluya_aclamacion: aleluya_aclamacion,
  evangelio_fuente: evangelio_fuente,
  evangelio: evangelio,
  oracion_delosfieles: oracion_delosfieles,
  oracion_ofrendas: oracion_ofrendas,
  oracion_comunion: oracion_comunion,
)
"""

WEB_SJB_TYP_CONTENT = """#import "template-web-sjb.typ": render-web-sjb
#import "common-defaults.typ": *
#import "{inc_file}": *

#render-web-sjb(
  tiempo: tiempo,
  domingo_num: domingo_num,
  fecha: fecha,
  frase: frase,
  oracion_colecta: oracion_colecta,
  lectura_primera_fuente: lectura_primera_fuente,
  lectura_primera: lectura_primera,
  salmo_fuente: salmo_fuente,
  salmo_partitura: salmo_partitura,
  salmo_aclamacion: salmo_aclamacion,
  salmo_estrofas: salmo_estrofas,
  lectura_segunda_fuente: lectura_segunda_fuente,
  lectura_segunda: lectura_segunda,
  aleluya_fuente: aleluya_fuente,
  aleluya_aclamacion: aleluya_aclamacion,
  evangelio_fuente: evangelio_fuente,
  evangelio: evangelio,
  oracion_delosfieles: oracion_delosfieles,
  oracion_ofrendas: oracion_ofrendas,
  oracion_comunion: oracion_comunion,
)
"""

# Output name pattern, wrapper template, and export format ("pdf" or "html").
TEMPLATES = {
    "sjb": ("misal-sjb-{date_compact}.pdf", SJB_TYP_CONTENT, "pdf"),
    "cjsjb": ("misal-cjsjb-{date_compact}.pdf", CJSJB_TYP_CONTENT, "pdf"),
    "web-sjb": ("misal-sjb-{date_compact}.html", WEB_SJB_TYP_CONTENT, "html"),
}

def compile_template(template_name: str, inc_file_name: str, date_compact: str):
    output_pattern, content_template, export_format = TEMPLATES[template_name]
    output_name = output_pattern.format(date_compact=date_compact)
    output_path = BASE_DIR / output_name

    typ_code = content_template.format(inc_file=inc_file_name)

    with tempfile.NamedTemporaryFile("w", dir=BASE_DIR, suffix=".typ", delete=False, encoding="utf-8") as tmp_file:
        tmp_file.write(typ_code)
        tmp_path = Path(tmp_file.name)

    try:
        cmd = ["typst", "compile"]
        if export_format == "html":
            # HTML export is still an experimental, feature-flagged target.
            cmd.extend(["--features", "html", "--format", "html", "--pretty"])
        if FONTS_DIR.exists():
            cmd.extend(["--font-path", str(FONTS_DIR)])
        cmd.extend([str(tmp_path), str(output_path)])

        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error compiling {output_name}:\n{res.stderr}", file=sys.stderr)
            return False
        print(f"Successfully compiled: {output_name}")
        return True
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
    # "all" means the printable missals; the web export stays opt-in
    # (--template web-sjb) until it has proven itself.
    templates_to_compile = ["sjb", "cjsjb"] if template == "all" else [template]
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
            "all = both printable missals (default: all)"
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
