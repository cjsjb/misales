#!/usr/bin/env python3
"""
build-index.py - Scans generated missals (PDF and web editions), builds the public
web portal (public/index.html) and copies into public/ everything the site needs.
"""

import csv
import html
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
PUBLIC_DIR = BASE_DIR / "public"
CALENDARIO_PATH = BASE_DIR / "calendario.csv"
FONTS_DIR = BASE_DIR / "fonts"

# Fonts the web edition loads (the @font-face blocks in styles.css). The site gets
# its own copy in public/fonts/, keeping the same relative paths, so the page
# looks the same in the repository and published.
WEB_FONTS = (
    "KumbhSans-VariableFont_YOPQ,wght.ttf",
    "Montserrat-Regular.otf",
    "Montserrat-Bold.otf",
)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Misales Parroquiales</title>
  <style>
    :root {{
      --primary: #2a6099;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #1e293b;
      --text-muted: #64748b;
      --border: #e2e8f0;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 2rem 1rem;
    }}
    .container {{
      max-width: 900px;
      margin: 0 auto;
    }}
    header {{
      text-align: center;
      margin-bottom: 3rem;
    }}
    h1 {{
      color: var(--primary);
      margin-bottom: 0.5rem;
    }}
    p.subtitle {{
      color: var(--text-muted);
      margin: 0;
    }}
    .date-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}
    .date-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.75rem;
      margin-bottom: 1rem;
    }}
    .date-title {{
      font-weight: bold;
      font-size: 1.2rem;
      color: var(--primary);
    }}
    .date-badge {{
      background: #e0f2fe;
      color: #0369a1;
      padding: 0.25rem 0.6rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 500;
    }}
    .downloads {{
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.6rem 1.2rem;
      border-radius: 6px;
      text-decoration: none;
      font-weight: 500;
      font-size: 0.95rem;
      transition: background-color 0.2s ease;
    }}
    .btn-sjb {{
      background-color: #2a6099;
      color: white;
    }}
    .btn-sjb:hover {{
      background-color: #1d4673;
    }}
    .btn-cjsjb {{
      background-color: #059669;
      color: white;
    }}
    .btn-cjsjb:hover {{
      background-color: #047857;
    }}
    .btn-web {{
      background-color: #5983b0;
      color: white;
    }}
    .btn-web:hover {{
      background-color: #42688f;
    }}
    footer {{
      text-align: center;
      margin-top: 3rem;
      color: var(--text-muted);
      font-size: 0.85rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Misales Parroquiales</h1>
      <p class="subtitle">Publicación automatizada de misales dominicales</p>
    </header>

    <main>
      {cards}
    </main>

    <footer>
      <p>Generado automáticamente con Typst & GitHub Actions</p>
    </footer>
  </div>
</body>
</html>
"""

CARD_TEMPLATE = """
<div class="date-card">
  <div class="date-header">
    <div class="date-title">{date_formatted} — Domingo {domingo_num} del Tiempo {tiempo}</div>
    <div class="date-badge">Ciclo {ciclo}</div>
  </div>
  <div class="downloads">
    {buttons}
  </div>
</div>
"""

def main():
    PUBLIC_DIR.mkdir(exist_ok=True)

    # 1. Gather dates from calendar
    calendar_data = []
    if CALENDARIO_PATH.exists():
        with open(CALENDARIO_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                calendar_data.append(row)

    # Sort in reverse chronological order (newest date first)
    calendar_data.sort(key=lambda x: x.get("fecha", "").strip(), reverse=True)

    cards_html = []
    web_published = False

    for row in calendar_data:
        formatted_date = row["fecha"].strip()
        date_compact = formatted_date.replace("-", "")
        tiempo = row["tiempo"].capitalize()
        domingo_num = row["numero"]
        ciclo = row["ciclo"].upper()

        buttons = []

        # Check for SJB PDF
        sjb_pdf_name = f"misal-sjb-{date_compact}.pdf"
        sjb_pdf_src = BASE_DIR / sjb_pdf_name
        if sjb_pdf_src.exists():
            shutil.copy2(sjb_pdf_src, PUBLIC_DIR / sjb_pdf_name)
            buttons.append(f'<a href="{sjb_pdf_name}" class="btn btn-sjb" target="_blank">📄 Misal SJB</a>')

        # Check for CJSJB PDF
        cjsjb_pdf_name = f"misal-cjsjb-{date_compact}.pdf"
        cjsjb_pdf_src = BASE_DIR / cjsjb_pdf_name
        if cjsjb_pdf_src.exists():
            shutil.copy2(cjsjb_pdf_src, PUBLIC_DIR / cjsjb_pdf_name)
            buttons.append(f'<a href="{cjsjb_pdf_name}" class="btn btn-cjsjb" target="_blank">📄 Misal CJSJB</a>')

        # Web edition: the same Sunday as the SJB sheet, tuned for the screen.
        # "haz-misal.py --all" builds it for every date.
        web_html_name = f"misal-sjb-{date_compact}.html"
        web_html_src = BASE_DIR / web_html_name
        if web_html_src.exists():
            shutil.copy2(web_html_src, PUBLIC_DIR / web_html_name)
            buttons.append(f'<a href="{web_html_name}" class="btn btn-web" target="_blank">🌐 Misal SJB (web)</a>')
            web_published = True

        if buttons:
            cards_html.append(CARD_TEMPLATE.format(
                date_formatted=html.escape(formatted_date),
                domingo_num=html.escape(str(domingo_num)),
                tiempo=html.escape(tiempo),
                ciclo=html.escape(ciclo),
                buttons="\n    ".join(buttons),
            ))

    # The web edition loads styles.css and its fonts, so the site needs its own
    # copy of both next to the HTML. The relative paths are the same in the
    # repository and in public/, so styles.css needs no rewriting.
    if web_published:
        shutil.copy2(BASE_DIR / "styles.css", PUBLIC_DIR / "styles.css")
        fonts_dest = PUBLIC_DIR / "fonts"
        fonts_dest.mkdir(exist_ok=True)
        for font in WEB_FONTS:
            shutil.copy2(FONTS_DIR / font, fonts_dest / font)
        print(f"Published web assets: styles.css + fonts/ ({len(WEB_FONTS)} files)")

    full_html = HTML_TEMPLATE.format(cards="\n".join(cards_html))
    index_path = PUBLIC_DIR / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Successfully generated web depot index (reverse sorted): {index_path}")

if __name__ == "__main__":
    main()
