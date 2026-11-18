#!/usr/bin/env python3
"""Build and validate the static presentation catalog."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
PRESENTATIONS = SITE / "presentations"
OUTPUT = SITE / "catalog.json"
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")
MAX_META_BYTES = 64 * 1024
MAX_TEXT_LENGTH = 500


def read_text_field(data: dict[str, Any], key: str, default: str = "") -> str:
    value = data.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"Metadatum '{key}' muss eine Zeichenkette sein.")
    value = value.strip()
    if len(value) > MAX_TEXT_LENGTH:
        raise ValueError(f"Metadatum '{key}' ist länger als {MAX_TEXT_LENGTH} Zeichen.")
    return value


def safe_thumbnail(folder: Path, value: Any, slug: str) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError(f"'{slug}': thumbnail muss eine Zeichenkette sein.")
    if "\\" in value:
        raise ValueError(f"'{slug}': thumbnail muss einen relativen URL-Pfad verwenden.")
    rel = PurePosixPath(value)
    if rel.is_absolute() or any(part in ("", ".", "..") for part in rel.parts):
        raise ValueError(f"'{slug}': ungültiger thumbnail-Pfad: {value}")
    target = folder.joinpath(*rel.parts)
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"'{slug}': thumbnail-Datei nicht gefunden oder nicht zulässig: {value}")
    try:
        target.resolve().relative_to(folder.resolve())
    except ValueError as exc:
        raise ValueError(f"'{slug}': thumbnail liegt außerhalb des Präsentationsordners.") from exc
    return value


def load_metadata(folder: Path, slug: str) -> dict[str, Any]:
    meta_file = folder / "meta.json"
    if not meta_file.exists():
        return {}
    if meta_file.is_symlink() or not meta_file.is_file():
        raise ValueError(f"'{slug}': meta.json darf keine symbolische Verknüpfung sein.")
    if meta_file.stat().st_size > MAX_META_BYTES:
        raise ValueError(f"'{slug}': meta.json ist größer als {MAX_META_BYTES} Bytes.")
    try:
        with meta_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"'{slug}': ungültiges JSON in meta.json: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"'{slug}': meta.json muss ein JSON-Objekt enthalten.")
    return data


def collect_presentations() -> list[dict[str, Any]]:
    PRESENTATIONS.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []

    for folder in sorted(PRESENTATIONS.iterdir(), key=lambda item: item.name.casefold()):
        if folder.is_symlink() or not folder.is_dir():
            continue

        index_file = folder / "index.html"
        if index_file.is_symlink():
            raise ValueError(f"'{folder.name}': index.html darf keine symbolische Verknüpfung sein.")
        if not index_file.is_file():
            continue

        slug = folder.name
        if not SLUG_PATTERN.fullmatch(slug):
            raise ValueError(
                f"Ungültiger Präsentationsordnername '{slug}'. Erlaubt: Kleinbuchstaben, Ziffern, '-' und '_'; "
                "maximal 63 Zeichen, erster Buchstabe/Ziffer."
            )

        meta = load_metadata(folder, slug)
        default_title = slug.replace("_", " ").replace("-", " ").title()
        title = read_text_field(meta, "title", default_title)
        description = read_text_field(meta, "description", "Keine Beschreibung vorhanden.")
        category = read_text_field(meta, "category", "Allgemein")
        presentation_date = read_text_field(meta, "date", "")

        if not title:
            raise ValueError(f"'{slug}': title darf nicht leer sein.")
        if presentation_date:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", presentation_date):
                raise ValueError(f"'{slug}': date muss das Format YYYY-MM-DD haben.")
            try:
                date.fromisoformat(presentation_date)
            except ValueError as exc:
                raise ValueError(f"'{slug}': date ist kein gültiges Kalenderdatum.") from exc

        tags = meta.get("tags", [])
        if not isinstance(tags, list) or len(tags) > 30:
            raise ValueError(f"'{slug}': tags muss eine Liste mit maximal 30 Einträgen sein.")
        clean_tags: list[str] = []
        for tag in tags:
            if not isinstance(tag, str) or not tag.strip() or len(tag.strip()) > 60:
                raise ValueError(f"'{slug}': jeder Tag muss Text mit 1 bis 60 Zeichen sein.")
            clean_tags.append(tag.strip())

        thumbnail = safe_thumbnail(folder, meta.get("thumbnail"), slug)

        entries.append({
            "slug": slug,
            "title": title,
            "description": description,
            "category": category,
            "date": presentation_date,
            "tags": clean_tags,
            "thumbnail": thumbnail,
        })

    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Prüft Präsentationen und erzeugt docs/catalog.json.")
    parser.add_argument("--check", action="store_true", help="Nur prüfen; catalog.json nicht verändern.")
    args = parser.parse_args()

    try:
        presentations = collect_presentations()
        catalog = {"schemaVersion": 1, "presentations": presentations}
        rendered = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"

        if args.check:
            if not OUTPUT.is_file():
                print(f"FEHLER: {OUTPUT.relative_to(ROOT)} fehlt. Ohne --check ausführen.", file=sys.stderr)
                return 1
            existing = OUTPUT.read_text(encoding="utf-8")
            if existing != rendered:
                print("FEHLER: catalog.json ist nicht aktuell. tools/build_catalog.py ausführen.", file=sys.stderr)
                return 1
            print(f"OK: {len(presentations)} Präsentationen geprüft; Katalog ist aktuell.")
            return 0

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        temporary = OUTPUT.with_suffix(".json.tmp")
        temporary.write_text(rendered, encoding="utf-8", newline="\n")
        temporary.replace(OUTPUT)
        print(f"OK: {len(presentations)} Präsentationen erfasst.")
        print(f"Katalog: {OUTPUT.relative_to(ROOT)}")
        return 0

    except (OSError, ValueError, TypeError) as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
