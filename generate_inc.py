#!/usr/bin/env python3
"""
generate_inc.py - Converts Markdown files in para-misales/ into Typst .inc files.

Usage:
    python3 generate_inc.py 2026-09-27
    python3 generate_inc.py 20260927
"""

import argparse
import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
PARA_MISALES_DIR = BASE_DIR / "para-misales"
CALENDARIO_PATH = BASE_DIR / "calendario.csv"

def normalize_date(date_str: str) -> tuple[str, str]:
    """
    Returns tuple of (formatted_date_with_dashes, compact_date_yyyymmdd).
    Accepts '2026-09-27' or '20260927'.
    """
    s = date_str.replace("-", "").strip()
    if len(s) != 8 or not s.isdigit():
        raise ValueError(f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD or YYYYMMDD.")
    formatted = f"{s[:4]}-{s[4:6]}-{s[6:]}"
    return formatted, s

def load_calendar(formatted_date: str) -> dict:
    """
    Looks up row in calendario.csv matching date.
    Returns dict with keys: fecha, ciclo, tiempo, numero, ocasion, color.
    """
    if not CALENDARIO_PATH.exists():
        raise FileNotFoundError(f"Calendar file not found: {CALENDARIO_PATH}")

    with open(CALENDARIO_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["fecha"].strip() == formatted_date:
                return row
    raise ValueError(f"Date '{formatted_date}' not found in {CALENDARIO_PATH}")

def parse_markdown_sections(file_path: Path) -> dict[str, str]:
    """
    Parses a markdown file into a dictionary of section title -> body content.
    Headings are expected as `# Heading Title`.
    """
    if not file_path.exists():
        return {}

    sections = {}
    current_title = None
    current_lines = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                if current_title is not None:
                    sections[current_title] = "\n".join(current_lines).strip()
                current_title = line[2:].strip()
                current_lines = []
            else:
                current_lines.append(line.rstrip("\r\n"))

        if current_title is not None:
            sections[current_title] = "\n".join(current_lines).strip()

    return sections

def parse_salmo_section(salmo_raw: str) -> tuple[str, str, list[str]]:
    """
    Parses `# Salmo` text content.
    Expects format:
      Salmo 24
      R: Descúbrenos, Señor, tus caminos.
      [Stanza 1 lines]
      [Empty line]
      [Stanza 2 lines]
    Returns (salmo_fuente, salmo_aclamacion, stanzas_list).
    """
    lines = salmo_raw.strip().split("\n")
    if not lines or not lines[0]:
        return "", "", []

    fuente_num = lines[0].strip()
    salmo_fuente = f"Del {fuente_num.lower()}." if not fuente_num.lower().startswith("del ") else fuente_num

    aclamacion = ""
    start_idx = 1
    for idx, line in enumerate(lines[1:], start=1):
        line_s = line.strip()
        if line_s.startswith("R:"):
            aclamacion = line_s[2:].strip()
            start_idx = idx + 1
            break

    # Group stanzas separated by empty lines
    stanzas = []
    current_stanza = []
    for line in lines[start_idx:]:
        if not line.strip():
            if current_stanza:
                stanzas.append("\n".join(current_stanza).strip())
                current_stanza = []
        else:
            current_stanza.append(line.rstrip())

    if current_stanza:
        stanzas.append("\n".join(current_stanza).strip())

    return salmo_fuente, aclamacion, stanzas

def parse_reading_section(section_raw: str) -> tuple[str, str]:
    """
    Parses Primera Lectura / Segunda Lectura / Evangelio section content.
    First non-empty line is the source citation.
    Remaining lines form the text body.
    """
    lines = [l.strip() for l in section_raw.strip().split("\n") if l.strip()]
    if not lines:
        return "", ""
    fuente = lines[0]
    cuerpo = "\n\n".join(lines[1:])
    return fuente, cuerpo

def format_typst_block(text: str, indent: str = "  ") -> str:
    """Formats multi-line text block as [#let var = [\n ... \n]]"""
    if not text:
        return ""
    indented_lines = "\n".join(f"{indent}{l}" if l else "" for l in text.split("\n"))
    return f"[\n{indented_lines}\n]"

def generate_inc_file(date_arg: str) -> Path:
    formatted_date, date_compact = normalize_date(date_arg)
    cal = load_calendar(formatted_date)

    tiempo = cal["tiempo"].capitalize()
    domingo_num = int(cal["numero"])
    ciclo = cal["ciclo"].upper()

    sjb_md_path = PARA_MISALES_DIR / f"{date_compact}-sjb.md"
    liturgia_md_path = PARA_MISALES_DIR / f"{cal['ciclo'].lower()}-{cal['tiempo'].lower()}-{domingo_num}-domingo.md"

    if not liturgia_md_path.exists():
        print(f"Warning: Liturgy file {liturgia_md_path.name} not found.", file=sys.stderr)

    sjb_sections = parse_markdown_sections(sjb_md_path)
    liturgia_sections = parse_markdown_sections(liturgia_md_path)

    frase = sjb_sections.get("Pregunta detonante", sjb_sections.get("Frase del domingo", sjb_sections.get("Frase", "")))
    monicion_entrada = sjb_sections.get("Mención de entrada", sjb_sections.get("Monición de entrada", ""))
    monicion_ofrendas = sjb_sections.get("Mención de ofrendas", sjb_sections.get("Monición de ofrendas", ""))
    oracion_universal = sjb_sections.get("Oración universal", "")
    oracion_personal = sjb_sections.get("Oración personal después de la comunión", "")
    # El eco y las demás secciones de reflexión también viven en <fecha>-sjb.md.
    eco_de_la_palabra = sjb_sections.get("Eco de la palabra", "")

    oracion_colecta = liturgia_sections.get("Oración colecta", "")
    oracion_ofrendas = liturgia_sections.get("Oración sobre las ofrendas", "")
    oracion_comunion = liturgia_sections.get("Oración después de la comunión", "")

    lectura_primera_fuente, lectura_primera = parse_reading_section(liturgia_sections.get("Primera lectura", ""))
    lectura_segunda_fuente, lectura_segunda = parse_reading_section(liturgia_sections.get("Segunda lectura", ""))
    evangelio_fuente, evangelio = parse_reading_section(liturgia_sections.get("Evangelio", ""))

    aleluya_aclamacion = liturgia_sections.get("Aclamación antes del evangelio", "")
    aleluya_lines = [l.strip() for l in aleluya_aclamacion.split("\n") if l.strip()]
    if len(aleluya_lines) > 1 and ("Jn " in aleluya_lines[0] or "Cfr" in aleluya_lines[0]):
        aleluya_aclamacion = "\n".join(aleluya_lines[1:])

    salmo_fuente, salmo_aclamacion, salmo_estrofas = parse_salmo_section(liturgia_sections.get("Salmo", ""))
    salmo_partitura_path = PARA_MISALES_DIR / f"{date_compact}-salmo.png"
    salmo_partitura_str = f"para-misales/{date_compact}-salmo.png" if salmo_partitura_path.exists() else "none"

    inc_lines = []
    inc_lines.append(f'#let tiempo = "{tiempo}"')
    inc_lines.append(f'#let domingo_num = {domingo_num}')
    inc_lines.append(f'#let fecha = "{formatted_date}"')
    inc_lines.append(f'#let frase = "{frase}"')
    inc_lines.append("")

    if monicion_entrada:
        inc_lines.append(f'#let monicion_entrada = [{monicion_entrada}]')
    if monicion_ofrendas:
        inc_lines.append(f'#let monicion_ofrendas = [{monicion_ofrendas}]')
    inc_lines.append("")

    if oracion_colecta:
        inc_lines.append(f'#let oracion_colecta = [{oracion_colecta}]')

    if lectura_primera_fuente:
        inc_lines.append(f'#let lectura_primera_fuente = [{lectura_primera_fuente}]')
        inc_lines.append(f'#let lectura_primera = {format_typst_block(lectura_primera)}')

    if salmo_fuente:
        inc_lines.append(f'#let salmo_fuente = "{salmo_fuente}"')
        if salmo_partitura_str != "none":
            inc_lines.append(f'#let salmo_partitura = "{salmo_partitura_str}"')
        else:
            inc_lines.append('#let salmo_partitura = none')
        inc_lines.append(f'#let salmo_aclamacion = "{salmo_aclamacion}"')

        inc_lines.append('#let salmo_estrofas = (')
        for estrofa in salmo_estrofas:
            inc_lines.append(f'  {format_typst_block(estrofa, indent="    ")},')
        inc_lines.append(')')

    if lectura_segunda_fuente:
        inc_lines.append(f'#let lectura_segunda_fuente = [{lectura_segunda_fuente}]')
        inc_lines.append(f'#let lectura_segunda = {format_typst_block(lectura_segunda)}')

    if aleluya_aclamacion:
        inc_lines.append(f'#let aleluya_aclamacion = [{aleluya_aclamacion}]')

    if evangelio_fuente:
        inc_lines.append(f'#let evangelio_fuente = [{evangelio_fuente}]')
        inc_lines.append(f'#let evangelio = {format_typst_block(evangelio)}')

    if oracion_universal:
        inc_lines.append(f'#let oracion_delosfieles = {format_typst_block(oracion_universal)}')

    if oracion_ofrendas:
        inc_lines.append(f'#let oracion_ofrendas = {format_typst_block(oracion_ofrendas)}')

    if oracion_comunion:
        inc_lines.append(f'#let oracion_comunion = {format_typst_block(oracion_comunion)}')

    if oracion_personal:
        inc_lines.append(f'#let oracion_personal = {format_typst_block(oracion_personal)}')

    if eco_de_la_palabra:
        inc_lines.append(f'#let eco_de_la_palabra = {format_typst_block(eco_de_la_palabra)}')

    output_path = BASE_DIR / f"{date_compact}.inc"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(inc_lines) + "\n")

    print(f"Successfully generated: {output_path.relative_to(BASE_DIR)}")
    return output_path

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
