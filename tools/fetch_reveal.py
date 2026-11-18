#!/usr/bin/env python3
"""Download and install the pinned reveal.js runtime distribution."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

VERSION = "6.0.2"
URL = f"https://github.com/hakimel/reveal.js/archive/refs/tags/{VERSION}.zip"
ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "vendor" / "reveal.js"
REQUIRED = [
    "reveal.js",
    "reveal.css",
    "reset.css",
    "theme/white.css",
    "plugin/markdown.js",
    "plugin/highlight.js",
    "plugin/notes.js",
]


def main() -> int:
    TARGET.mkdir(parents=True, exist_ok=True)
    print(f"Lade offizielles reveal.js-Release {VERSION} ...")
    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "offline-reveal-presentation-library/1.0"},
    )

    try:
        with tempfile.TemporaryDirectory(prefix="reveal-install-") as tmp_name:
            tmp = Path(tmp_name)
            archive_path = tmp / "reveal.zip"
            with urllib.request.urlopen(request, timeout=60) as response, archive_path.open("wb") as out:
                shutil.copyfileobj(response, out)

            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
                package_name = next(
                    (name for name in names if name.endswith("/package.json") and name.count("/") == 1),
                    None,
                )
                if package_name is None:
                    raise RuntimeError("package.json wurde im Release-Archiv nicht gefunden.")
                package = json.loads(archive.read(package_name).decode("utf-8"))
                if package.get("version") != VERSION:
                    raise RuntimeError(
                        f"Versionsprüfung fehlgeschlagen: erwartet {VERSION}, erhalten {package.get('version')}"
                    )

                archive_root = package_name.rsplit("/", 1)[0] + "/"
                dist_prefix = archive_root + "dist/"
                staging_dist = tmp / "dist"
                staging_dist.mkdir()

                copied = set()
                for info in archive.infolist():
                    name = info.filename
                    if not name.startswith(dist_prefix) or info.is_dir():
                        continue
                    relative = name[len(dist_prefix):]
                    rel_path = PurePosixPath(relative)
                    if rel_path.is_absolute() or any(part in ("", ".", "..") for part in rel_path.parts):
                        raise RuntimeError(f"Unsicherer Archivpfad: {name}")
                    destination = staging_dist.joinpath(*rel_path.parts)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as src, destination.open("wb") as dst:
                        shutil.copyfileobj(src, dst)
                    copied.add(relative)

                missing = [item for item in REQUIRED if item not in copied]
                if missing:
                    raise RuntimeError("Im Release fehlen benötigte Dateien: " + ", ".join(missing))

                license_member = next(
                    (name for name in names if name in (archive_root + "LICENSE", archive_root + "LICENSE.md")),
                    None,
                )
                if license_member:
                    license_text = archive.read(license_member)
                else:
                    license_text = b"See the official reveal.js repository for license information.\n"

                # Replace only after the archive has passed the checks above.
                final_dist = TARGET / "dist"
                old_dist = TARGET / "dist.previous"
                if old_dist.exists():
                    shutil.rmtree(old_dist)
                if final_dist.exists():
                    final_dist.rename(old_dist)
                try:
                    shutil.move(str(staging_dist), str(final_dist))
                except Exception:
                    if old_dist.exists() and not final_dist.exists():
                        old_dist.rename(final_dist)
                    raise
                if old_dist.exists():
                    shutil.rmtree(old_dist)
                (TARGET / "LICENSE").write_bytes(license_text)
                (TARGET / "VERSION").write_text(VERSION + "\n", encoding="utf-8")

        print(f"reveal.js {VERSION} wurde installiert unter:")
        print(TARGET / "dist")
        print("Ab jetzt kann die Bibliothek ohne Internetverbindung betrieben werden.")
        return 0

    except Exception as exc:
        print(f"Installation fehlgeschlagen: {exc}", file=sys.stderr)
        print("Prüfe die Internetverbindung und versuche es erneut.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
