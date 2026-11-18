#!/usr/bin/env python3
"""Create a presentation folder from the repository template."""
from __future__ import annotations

import argparse
from html import escape
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "presentation"
DESTINATION = ROOT / "docs" / "presentations"
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Neue reveal.js-Präsentation aus Vorlage anlegen.")
    parser.add_argument("slug", help="Ordnername, z. B. produktstrategie")
    parser.add_argument("--title", default=None)
    parser.add_argument("--category", default="Allgemein")
    parser.add_argument("--description", default="Neue Präsentation.")
    args = parser.parse_args()

    if not SLUG_PATTERN.fullmatch(args.slug):
        parser.error("Slug: nur Kleinbuchstaben, Ziffern, '-' und '_'; max. 63 Zeichen.")

    target = DESTINATION / args.slug
    if target.exists():
        parser.error(f"Zielordner existiert bereits: {target}")

    title = args.title or args.slug.replace("_", " ").replace("-", " ").title()
    DESTINATION.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE, target)

    meta = {
        "title": title,
        "description": args.description,
        "category": args.category,
        "date": date.today().isoformat(),
        "tags": [],
        "thumbnail": "media/thumbnail.svg",
    }
    (target / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    html_path = target / "index.html"
    html = html_path.read_text(encoding="utf-8")
    html_escape_title = escape(title, quote=True)
    html = html.replace("{{PRESENTATION_TITLE}}", html_escape_title)
    html_path.write_text(html, encoding="utf-8")

    print(f"Präsentation angelegt: {target.relative_to(ROOT)}")
    print("Katalog aktualisieren und lokal starten: python tools/serve.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
