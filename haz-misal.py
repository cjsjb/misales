#!/usr/bin/env python3
"""
haz-misal.py - Generates .inc files and compiles missal PDFs.

Usage:
    python3 haz-misal.py 2026-09-27
    python3 haz-misal.py 2026-09-27 --template sjb
    python3 haz-misal.py --all
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from generate_inc import generate_inc_file, normalize_date

BASE_DIR = Path(__file__).parent.resolve()

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

TEMPLATES = {
    "sjb": ("misal-sjb-{date_compact}.pdf", SJB_TYP_CONTENT),
    "cjsjb": ("misal-cjsjb-{date_compact}.pdf", CJSJB_TYP_CONTENT),
}

def compile_template(template_name: str, inc_file_name: str, date_compact: str):
    pdf_filename, content_template = TEMPLATES[template_name]
    output_pdf_name = pdf_filename.format(date_compact=date_compact)
    output_pdf_path = BASE_DIR / output_pdf_name

    typ_code = content_template.format(inc_file=inc_file_name)

    # Create temporary .typ file inside BASE_DIR so relative imports (e.g. template-sjb.typ) work smoothly
    with tempfile.NamedTemporaryFile("w", dir=BASE_DIR, suffix=".typ", delete=False, encoding="utf-8") as tmp_file:
        tmp_file.write(typ_code)
        tmp_path = Path(tmp_file.name)

    try:
        cmd = ["typst", "compile", str(tmp_path), str(output_pdf_path)]
        res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error compiling {output_pdf_name}:\n{res.stderr}", file=sys.stderr)
            return False
        print(f"Successfully compiled: {output_pdf_name}")
        return True
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

def main():
    parser = argparse.ArgumentParser(description="Build missal PDFs for a given date.")
    parser.add_argument("date", help="Date in YYYY-MM-DD or YYYYMMDD format (e.g. 2026-09-27)")
    parser.add_argument(
        "--template",
        choices=["sjb", "cjsjb", "all"],
        default="all",
        help="Template to compile (default: all)",
    )
    args = parser.parse_args()

    try:
        formatted_date, date_compact = normalize_date(args.date)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 1. Generate .inc file
    inc_path = generate_inc_file(args.date)

    # 2. Compile PDF(s)
    templates_to_compile = ["sjb", "cjsjb"] if args.template == "all" else [args.template]
    success = True
    for t_name in templates_to_compile:
        if not compile_template(t_name, inc_path.name, date_compact):
            success = False

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
