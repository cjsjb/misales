#!/usr/bin/env python3
"""
misal.py - Shared constants, utilities, and workflow functions for the misal toolchain.

Imported by: generate_inc.py, haz-misal.py, haz-misal-mensual.py, build-index.py.
"""

import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.resolve()
CALENDARIO_PATH = BASE_DIR / "calendario.csv"
FONTS_DIR = BASE_DIR / "fonts"
PARA_MISALES_DIR = BASE_DIR / "para-misales"
PUBLIC_DIR = BASE_DIR / "public"

# ── Weekday data ─────────────────────────────────────────────────────────────

DIAS_SEMANA = (
    "lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo",
)
# The markdown filename may or may not carry a tilde; both forms are tried.
DIAS_SEMANA_CON_TILDE = {"miercoles": "miércoles", "sabado": "sábado"}

# ── Liturgical colors ───────────────────────────────────────────────────────

COLORES_VALIDOS = ("verde", "morado", "blanco", "rojo")

# Default color per liturgical season (the `tiempo` column in calendario.csv).
# Exceptions (Palm Sunday, Pentecost, a saint's feast) go in the `Color`
# section of the liturgy file.
COLORES_TIEMPO = {
    "ordinario": "verde",
    "adviento": "morado",
    "cuaresma": "morado",
    "navidad": "blanco",
    "pascua": "blanco",
}
COLOR_POR_DEFECTO = "verde"

# Occasions that are never printed on the cover: the title already names the day
# ("XXVII DOMINGO DEL TIEMPO ORDINARIO") or there is no celebration to announce.
OCASIONES_ORDINARIAS = ("feria", "domingo")

# Regular data sections: brought from the general day sheet, overridable by the
# date-specific sheet.
SECCIONES_REGULARES = (
    "Color",
    "Ocasión",
    "Primera lectura",
    "Segunda lectura",
    "Salmo",
    "Aclamación antes del evangelio",
    "Evangelio",
    "Oración colecta",
    "Oración sobre las ofrendas",
    "Oración después de la comunión",
)

# ── Typst wrapper templates (shared by haz-misal.py and haz-misal-mensual.py) ─

# Ajustes de página y texto del misal impreso, que define common.typ. Se piden al
# principio del documento, una sola vez: no pueden ir dentro de la plantilla,
# porque cada `set page` que entra en vigor inserta una página nueva y la
# plantilla se llama una vez por día en el misal mensual.
AJUSTES_MISAL = '#import "common.typ": ajustes_misal\n#show: ajustes_misal\n'

SJB_TYP_CONTENT = """{ajustes}
#import "template-sjb.typ": render-sjb
#import "common-defaults.typ": *
#import "{inc_file}": *

#render-sjb(
  tiempo: tiempo,
  domingo_num: domingo_num,
  fecha: fecha,
  frase: frase,
  ocasion: ocasion,
  color_liturgico: color_liturgico,
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
  oracion_personal: oracion_personal,
  eco_de_la_palabra: eco_de_la_palabra,
  portada: {portada},
  separador: {separador},
  mensual: {mensual},
)
"""

# CJSJB: the Bosque community missal (includes cantos).
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

# Web edition: only for haz-misal.py — the monthly booklet uses SJB_TYP_CONTENT.
WEB_SJB_TYP_CONTENT = """#import "template-web-sjb.typ": render-web-sjb
#import "common-defaults.typ": *
#import "{inc_file}": *

#render-web-sjb(
  tiempo: tiempo,
  domingo_num: domingo_num,
  fecha: fecha,
  frase: frase,
  ocasion: ocasion,
  color_liturgico: color_liturgico,
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
  oracion_personal: oracion_personal,
  eco_de_la_palabra: eco_de_la_palabra,
  entre_lineas_sagradas: entre_lineas_sagradas,
  lo_sabias: lo_sabias,
)
"""

# Output name pattern, wrapper template, and export format ("pdf" or "html").
TEMPLATES = {
    "sjb": ("misal-sjb-{date_compact}.pdf", SJB_TYP_CONTENT, "pdf"),
    "cjsjb": ("misal-cjsjb-{date_compact}.pdf", CJSJB_TYP_CONTENT, "pdf"),
    "web-sjb": ("misal-sjb-{date_compact}.html", WEB_SJB_TYP_CONTENT, "html"),
}

# ── Date helpers ─────────────────────────────────────────────────────────────

def normalize_date(date_str: str) -> tuple[str, str]:
    """
    Returns (formatted_date_with_dashes, compact_date_yyyymmdd).
    Accepts '2026-09-27' or '20260927'.
    """
    s = date_str.replace("-", "").strip()
    if len(s) != 8 or not s.isdigit():
        raise ValueError(f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD or YYYYMMDD.")
    formatted = f"{s[:4]}-{s[4:6]}-{s[6:]}"
    return formatted, s


def load_calendar(formatted_date: str) -> dict:
    """
    Look up row in calendario.csv matching date.
    Returns dict with keys: fecha, ciclo, tiempo, numero.
    """
    if not CALENDARIO_PATH.exists():
        raise FileNotFoundError(f"Calendar file not found: {CALENDARIO_PATH}")

    with open(CALENDARIO_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["fecha"].strip() == formatted_date:
                return row
    raise ValueError(f"Date '{formatted_date}' not found in {CALENDARIO_PATH}")


# ── Weekday and Roman numerals ──────────────────────────────────────────────

def dia_semana_es(formatted_date: str) -> str:
    """
    Returns the weekday of the date in Spanish, capitalised: «Lunes»,
    «Miércoles», «Sábado».
    """
    dia = DIAS_SEMANA[datetime.strptime(formatted_date, "%Y-%m-%d").weekday()]
    return DIAS_SEMANA_CON_TILDE.get(dia, dia).capitalize()


# Roman numerals: 27 → «XXVII»
ROMANOS = ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
           (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
           (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))


def romano(numero: int) -> str:
    """
    Returns the number in Roman numerals: 27 → «XXVII».
    Covers the tens up to 39 needed for the Sundays of the year.
    """
    resultado = ""
    resto = numero
    for valor, letra in ROMANOS:
        while resto >= valor:
            resultado += letra
            resto -= valor
    return resultado


# ── Liturgy file resolution ─────────────────────────────────────────────────

def find_liturgia_md(formatted_date: str, ciclo: str, tiempo: str, numero: int) -> Path:
    """
    Returns the .md of the day's liturgy: <ciclo>-<tiempo>-<número>-<weekday>.md.
    A feria (weekday) is not the Sunday of that week: Monday 5 Oct 2026 uses
    a-ordinario-27-lunes.md, not a-ordinario-27-domingo.md.
    """
    dia = DIAS_SEMANA[datetime.strptime(formatted_date, "%Y-%m-%d").weekday()]
    base = f"{ciclo.lower()}-{tiempo.lower()}-{numero}"
    candidatos = [dia]
    if dia in DIAS_SEMANA_CON_TILDE:
        candidatos.append(DIAS_SEMANA_CON_TILDE[dia])
    for candidato in candidatos:
        ruta = PARA_MISALES_DIR / f"{base}-{candidato}.md"
        if ruta.exists():
            return ruta
    # If none exists, return the expected path so the warning names it.
    return PARA_MISALES_DIR / f"{base}-{dia}.md"


# ── Liturgical color & occasion ─────────────────────────────────────────────

def resolver_color(color_md: str, tiempo: str) -> str:
    """
    Returns the name of the day's liturgical color.

    The liturgy's `Color` section wins when it holds a known name; otherwise the
    color comes from the liturgical season (`tiempo`). An unrecognized value is
    reported instead of guessed, and falls back to the season color.
    """
    valor = color_md.strip().lower()
    if valor:
        if valor in COLORES_VALIDOS:
            return valor
        print(
            f"Warning: unrecognized liturgical color '{color_md.strip()}'; "
            f"using the color of the season instead.",
            file=sys.stderr,
        )
    return COLORES_TIEMPO.get(tiempo.strip().lower(), COLOR_POR_DEFECTO)


def resolver_ocasion(ocasion_md: str) -> str | None:
    """
    Returns the occasion to print under the cover date, or None when there is
    nothing to say.

    Any word carrying a colon is dropped — the rank goes marked that way
    ("Memoria:", "Fiesta:", "Solemnidad:") and the cover names the celebration,
    not its degree. Ordinary days say nothing.
    """
    texto = " ".join(p for p in ocasion_md.split() if ":" not in p).strip()
    if not texto or texto.lower() in OCASIONES_ORDINARIAS:
        return None
    return texto


# ── Markdown parsing ────────────────────────────────────────────────────────

def parse_markdown_sections(file_path: Path) -> dict[str, str]:
    """
    Parse a Markdown file into a dict of section title → body content.
    Headings are expected as `# Heading Title`.
    Returns {} if the file does not exist.
    """
    if not file_path.exists():
        return {}

    sections: dict[str, str] = {}
    current_title = None
    current_lines: list[str] = []

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
    Parse `# Salmo` text content.
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

    # Group stanzas separated by empty lines.
    stanzas: list[str] = []
    current_stanza: list[str] = []
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
    Parse Primera Lectura / Segunda Lectura / Evangelio section content.
    First non-empty line is the source citation, returned with its final full stop.
    Remaining lines form the text body, keeping the paragraph breaks.
    """
    lines = [l.strip() for l in section_raw.strip().split("\n") if l.strip()]
    if not lines:
        return "", ""
    fuente = asegurar_punto_final(lines[0])
    cuerpo = "\n\n".join(lines[1:])
    return fuente, cuerpo


def format_typst_block(text: str, indent: str = "  ") -> str:
    """
    Format multi-line text block as [#let var = [\n ... \n]].
    """
    if not text:
        return ""
    indented_lines = "\n".join(f"{indent}{l}" if l else "" for l in text.split("\n"))
    return f"[\n{indented_lines}\n]"


# ── Helpers ──────────────────────────────────────────────────────────────────

def asegurar_punto_final(texto: str) -> str:
    """
    Return the citation ending in a full stop: some sheets write it without one
    («Del santo Evangelio según san Mateo 22, 34-40») and the missal prints it.
    """
    texto = texto.strip()
    if texto and not texto.endswith("."):
        return texto + "."
    return texto


def secciones_regulares(sjb_sections: dict[str, str], liturgia_sections: dict[str, str]) -> dict[str, str]:
    """
    Merge the day's regular data, with the date-specific sheet on top.

    The regular data — colour, occasion, prayers, readings, psalm — comes from
    <ciclo>-<tiempo>-<numero>-<weekday>.md, the general sheet of the day. When
    <date>-sjb.md, the sheet of that exact date, carries one of those sections,
    it wins: that is how a parish feast brings its own prayers and readings. A
    regular section that only the date sheet has is added as well.

    Returns the general sheet's sections with the date sheet's on top.
    """
    fusion = dict(liturgia_sections)
    for titulo in SECCIONES_REGULARES:
        valor = sjb_sections.get(titulo, "")
        if valor:
            fusion[titulo] = valor
    return fusion


# ── .inc generation ─────────────────────────────────────────────────────────

def generate_inc_file(date_arg: str) -> Path:
    """
    Generate a Typst .inc file from Markdown liturgy sources.

    Returns the path of the generated file.
    """
    formatted_date, date_compact = normalize_date(date_arg)
    cal = load_calendar(formatted_date)

    tiempo = cal["tiempo"].capitalize()
    domingo_num = int(cal["numero"])
    ciclo = cal["ciclo"].upper()

    sjb_md_path = PARA_MISALES_DIR / f"{date_compact}-sjb.md"
    liturgia_md_path = find_liturgia_md(formatted_date, cal["ciclo"], cal["tiempo"], domingo_num)

    if not liturgia_md_path.exists():
        print(f"Warning: Liturgy file {liturgia_md_path.name} not found.", file=sys.stderr)

    sjb_sections = parse_markdown_sections(sjb_md_path)
    liturgia_sections = parse_markdown_sections(liturgia_md_path)
    liturgia_del_dia = secciones_regulares(sjb_sections, liturgia_sections)

    frase = sjb_sections.get("Pregunta detonante", sjb_sections.get("Frase del domingo", sjb_sections.get("Frase", "")))
    monicion_entrada = sjb_sections.get("Mención de entrada", sjb_sections.get("Monición de entrada", ""))
    monicion_ofrendas = sjb_sections.get("Mención de ofrendas", sjb_sections.get("Monición de ofrendas", ""))
    oracion_universal = sjb_sections.get("Oración universal", "")
    oracion_personal = sjb_sections.get("Oración personal después de la comunión", "")
    eco_de_la_palabra = sjb_sections.get("Eco de la palabra", "")
    entre_lineas_sagradas = sjb_sections.get("Entre líneas sagradas", "")
    lo_sabias = sjb_sections.get("Cápsula para saber más", "")

    oracion_colecta = liturgia_del_dia.get("Oración colecta", "")
    oracion_ofrendas = liturgia_del_dia.get("Oración sobre las ofrendas", "")
    oracion_comunion = liturgia_del_dia.get("Oración después de la comunión", "")

    color_md = liturgia_del_dia.get("Color", "")
    color_liturgico = resolver_color(color_md, cal["tiempo"])

    occasion = resolver_ocasion(liturgia_del_dia.get("Ocasión", ""))

    lectura_primera_fuente, lectura_primera = parse_reading_section(liturgia_del_dia.get("Primera lectura", ""))
    lectura_segunda_fuente, lectura_segunda = parse_reading_section(liturgia_del_dia.get("Segunda lectura", ""))
    evangelio_fuente, evangelio = parse_reading_section(liturgia_del_dia.get("Evangelio", ""))

    aleluya_fuente, aleluya_aclamacion = parse_reading_section(
        liturgia_del_dia.get("Aclamación antes del evangelio", "")
    )

    salmo_fuente, salmo_aclamacion, salmo_estrofas = parse_salmo_section(liturgia_del_dia.get("Salmo", ""))
    salmo_partitura_path = PARA_MISALES_DIR / f"{date_compact}-salmo.png"
    salmo_partitura_str = f"para-misales/{date_compact}-salmo.png" if salmo_partitura_path.exists() else "none"

    inc_lines = []
    inc_lines.append(f'#let tiempo = "{tiempo}"')
    inc_lines.append(f'#let domingo_num = {domingo_num}')
    inc_lines.append(f'#let fecha = "{formatted_date}"')
    inc_lines.append(f'#let frase = "{frase}"')
    if occasion:
        inc_lines.append(f'#let ocasion = "{occasion}"')
    else:
        inc_lines.append("#let ocasion = none")
    inc_lines.append(f'#let color_liturgico = "{color_liturgico}"')
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
        inc_lines.append(f'#let aleluya_fuente = [{aleluya_fuente}]')
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

    if entre_lineas_sagradas:
        inc_lines.append(f'#let entre_lineas_sagradas = {format_typst_block(entre_lineas_sagradas)}')

    if lo_sabias:
        inc_lines.append(f'#let lo_sabias = {format_typst_block(lo_sabias)}')

    output_path = BASE_DIR / f"{date_compact}.inc"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(inc_lines) + "\n")

    print(f"Successfully generated: {output_path.relative_to(BASE_DIR)}")
    return output_path


# ── Typst compilation ───────────────────────────────────────────────────────

def compilar_typst(typ_path: Path, output_path: Path, export_format: str = "pdf") -> bool:
    """
    Compile a .typ file into output_path ("pdf" or "html") and report success.
    """
    cmd = ["typst", "compile"]
    if export_format == "html":
        cmd.extend(["--features", "html", "--format", "html", "--pretty"])
    if FONTS_DIR.exists():
        cmd.extend(["--font-path", str(FONTS_DIR)])
    cmd.extend([str(typ_path), str(output_path)])

    res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error compiling {output_path.name}:\n{res.stderr}", file=sys.stderr)
        return False
    print(f"Successfully compiled: {output_path.name}")
    return True


def typst_bool(valor: bool) -> str:
    """
    Return the Typst spelling of a boolean.
    Typst writes true/false in lower case.
    """
    return "true" if valor else "false"
