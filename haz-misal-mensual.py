#!/usr/bin/env python3
"""
haz-misal-mensual.py - Builds one printable booklet with every day the calendar
lists for a month: the days one after another, each one laid out by the same
template as the daily missal, with an unmodified cover for the first day and an
inline date separator at the top of every following day.

Usage:
    python3 haz-misal-mensual.py 2026-10
    python3 haz-misal-mensual.py 2026-10 --keep-typ
"""

import argparse
import csv
import importlib.util
import re
import sys
from pathlib import Path

from generate_inc import (
    CALENDARIO_PATH,
    DIAS_SEMANA,
    PARA_MISALES_DIR,
    find_liturgia_md,
    generate_inc_file,
    load_calendar,
)

BASE_DIR = Path(__file__).parent.resolve()

# Las hojas de liturgia se llaman <ciclo>-<tiempo>-<número>-<día>.md. Las de
# reflexión (20260927-sjb.md) no entran: llevan fecha en el propio nombre y no
# son la liturgia del día.
PATRON_HOJA = re.compile(r"^(?P<ciclo>[a-z]+)-(?P<tiempo>[a-z]+)-(?P<numero>\d+)-(?P<dia>[a-z]+)$")

def cargar_haz_misal():
    """
    Loads haz-misal.py by path: the name has a hyphen, so it cannot be imported
    the usual way, and the monthly booklet reuses its Typst wrapper instead of
    repeating the twenty-odd template arguments.
    """
    ruta = BASE_DIR / "haz-misal.py"
    spec = importlib.util.spec_from_file_location("haz_misal", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo

haz_misal = cargar_haz_misal()

def normalize_month(mes: str) -> tuple[int, int, str]:
    """
    Returns (year, month_number, compact_month_yyyymm) for 'YYYY-MM' or 'YYYYMM'.
    """
    s = mes.replace("-", "").replace("/", "").strip()
    if len(s) != 6 or not s.isdigit():
        raise ValueError(f"Invalid month format: '{mes}'. Expected YYYY-MM or YYYYMM.")
    anio, numero_mes = int(s[:4]), int(s[4:])
    if not 1 <= numero_mes <= 12:
        raise ValueError(f"Invalid month: '{mes}'. Months run from 1 to 12.")
    return anio, numero_mes, s

def fechas_del_mes(anio: int, numero_mes: int) -> list[str]:
    """Returns the dates of calendario.csv that fall in that month, oldest first."""
    if not CALENDARIO_PATH.exists():
        raise FileNotFoundError(f"Calendar file not found: {CALENDARIO_PATH}")

    prefijo = f"{anio:04d}-{numero_mes:02d}-"
    fechas = []
    with open(CALENDARIO_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fecha = (row.get("fecha") or "").strip()
            if fecha.startswith(prefijo):
                fechas.append(fecha)
    return sorted(fechas)

def avisar_de_lo_que_sobra(fechas: list[str], compacto: str) -> list[str]:
    """
    Reports prepared data the calendar does not list, so that a day with a sheet
    ready never disappears from the booklet in silence:

    - .inc files of the month that were not picked: days built before and still
      on disk, whose date is no longer in the calendar.
    - liturgy sheets whose weekday is missing from the month's dates. A loose
      sheet (a-ordinario-27-jueves.md) carries no date in its name, so the only
      way to tell it apart is to compare weekday and number with the month; if
      the number is not one of the month's, the sheet belongs to another month
      and is left alone. That is how the Thursday sheet of week 27 shows up.
    """
    avisos = []

    for ruta in sorted(BASE_DIR.glob(f"{compacto}*.inc")):
        fecha = f"{ruta.name[:4]}-{ruta.name[4:6]}-{ruta.name[6:8]}"
        if fecha not in fechas:
            avisos.append(f"generado pero fuera del calendario: {ruta.name}")

    numeros = set()
    usadas = set()
    for fecha in fechas:
        row = load_calendar(fecha)
        numero = int(row["numero"])
        numeros.add(numero)
        usadas.add(find_liturgia_md(fecha, row["ciclo"], row["tiempo"], numero).name)

    for ruta in sorted(PARA_MISALES_DIR.glob("*.md")):
        hoja = PATRON_HOJA.match(ruta.stem)
        if not hoja or ruta.name in usadas:
            continue
        if int(hoja.group("numero")) in numeros and hoja.group("dia") in DIAS_SEMANA:
            avisos.append(f"hoja preparada que el calendario no lista: {ruta.name}")

    for aviso in avisos:
        print(f"Aviso: {aviso}", file=sys.stderr)
    return avisos

def escribir_dia(fecha: str, indice: int, compacto: str) -> Path:
    """
    Writes the .typ of one day: the daily wrapper, asking the template for the
    date separator, which every day carries — the first one included, right after
    the cover.

    Returns the path of the generated file.
    """
    portada = indice == 1
    inc_path = generate_inc_file(fecha)

    # El separador lo pinta la plantilla, dentro de su propio ámbito de página:
    # aquí sólo se dice que lo lleva. Lo llevan todos los días, también el
    # primero: la portada abre el cuaderno y el día 1 abre con su separador, como
    # los demás. Nada de saltos ni de fecha sueltos en el envoltorio, que saldrían
    # con las propiedades de página por omisión.
    # Los ajustes de página tampoco van aquí: los incluye el maestro una sola vez,
    # porque cada `set page` que entra en vigor abre página nueva.
    typ_code = haz_misal.SJB_TYP_CONTENT.format(
        inc_file=inc_path.name,
        portada=haz_misal.typst_bool(portada),
        # La portada del cuaderno es la del primer día: sólo ése dice «Misal
        # Mensual» y el mes.
        mensual=haz_misal.typst_bool(portada),
        separador=haz_misal.typst_bool(True),
        ajustes="",
    )

    ruta = BASE_DIR / f"misal-mensual-{compacto}-d{indice:02d}.typ"
    ruta.write_text(typ_code, encoding="utf-8")
    return ruta

def escribir_maestro(dias: list[Path], compacto: str) -> Path:
    """
    Writes the master file: one included day per block.

    Cada día va en su propio bloque para que las definiciones de un día no
    lleguen al siguiente: los .inc de todos los días usan los mismos nombres
    (lectura_primera, evangelio…) y en un mismo ámbito se pisarían. El bloque
    devuelve el contenido del día, que se inserta tal cual.
    """
    # Los ajustes de página van una sola vez, al principio del maestro, y no en
    # cada día: cada `set page` que entra en vigor abre página nueva, así que en
    # cada día partían el misal en una página por día.
    lineas = [f'#{{\n  include("{ruta.name}")\n}}' for ruta in dias]
    ruta = BASE_DIR / f"misal-sjb-mensual-{compacto}.typ"
    contenido = haz_misal.AJUSTES_MISAL + "\n" + "\n".join(lineas) + "\n"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta

def main():
    parser = argparse.ArgumentParser(
        description="Builds one monthly booklet with every day the calendar lists for that month."
    )
    parser.add_argument("mes", help="Month in YYYY-MM or YYYYMM format (e.g. 2026-10)")
    parser.add_argument(
        "--keep-typ",
        action="store_true",
        help="Keep the generated .typ files in the repository root so they can be read or recompiled",
    )
    args = parser.parse_args()

    try:
        anio, numero_mes, compacto = normalize_month(args.mes)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        fechas = fechas_del_mes(anio, numero_mes)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not fechas:
        print(f"Error: no dates for {anio:04d}-{numero_mes:02d} in {CALENDARIO_PATH}", file=sys.stderr)
        sys.exit(1)

    avisar_de_lo_que_sobra(fechas, compacto)

    print(f"Misal mensual {anio:04d}-{numero_mes:02d}: {len(fechas)} día(s) en el calendario")

    escritos: list[Path] = []
    fallos: list[str] = []
    maestro: Path | None = None
    compilado = False

    try:
        for indice, fecha in enumerate(fechas, start=1):
            try:
                escritos.append(escribir_dia(fecha, indice, compacto))
            except (ValueError, FileNotFoundError) as e:
                print(f"Error en {fecha}: {e}", file=sys.stderr)
                fallos.append(fecha)

        if not escritos:
            print("Error: no day could be generated", file=sys.stderr)
            sys.exit(1)

        maestro = escribir_maestro(escritos, compacto)
        salida = BASE_DIR / f"misal-sjb-mensual-{compacto}.pdf"
        compilado = haz_misal.compilar_typst(maestro, salida, "pdf")
    finally:
        if args.keep_typ:
            print("Ficheros .typ conservados en el directorio del proyecto:")
            for ruta in escritos + ([maestro] if maestro else []):
                print(f"  {ruta.name}")
        else:
            for ruta in escritos + ([maestro] if maestro else []):
                ruta.unlink(missing_ok=True)

    if fallos:
        print(f"Días sin generar: {', '.join(fallos)}", file=sys.stderr)
    if not compilado or fallos:
        sys.exit(1)

if __name__ == "__main__":
    main()
