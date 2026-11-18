#!/usr/bin/env python3
"""Build the catalog and serve docs/ on the local machine only."""
from __future__ import annotations

import argparse
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
TOOLS = ROOT / "tools"


class LocalHandler(SimpleHTTPRequestHandler):
    server_version = "PresentationLibrary/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def translate_path(self, path: str) -> str:
        # Resolve requests under docs/ only. This also prevents local symlinks
        # from exposing files outside the project through the development server.
        raw_path = unquote(urlsplit(path).path).replace("\\", "/")
        if "\x00" in raw_path:
            return str(SITE / "__not_found__")
        parts = [part for part in PurePosixPath(raw_path).parts if part != "/"]
        if any(part in ("", ".", "..") or ":" in part for part in parts):
            return str(SITE / "__not_found__")
        candidate = SITE.joinpath(*parts)
        try:
            resolved = candidate.resolve()
            resolved.relative_to(SITE.resolve())
        except (OSError, ValueError):
            return str(SITE / "__not_found__")
        return str(candidate)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def main() -> int:
    parser = argparse.ArgumentParser(description="Lokaler Webserver für die Präsentationsbibliothek.")
    parser.add_argument("--host", default="127.0.0.1", help="Standard: 127.0.0.1 (nur dieser Rechner)")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if not (1 <= args.port <= 65535):
        parser.error("Port muss zwischen 1 und 65535 liegen.")
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        parser.error("Aus Sicherheitsgründen ist nur localhost als Host erlaubt.")

    reveal_runtime = SITE / "vendor" / "reveal.js" / "dist" / "reveal.js"
    if not reveal_runtime.is_file():
        print("FEHLER: reveal.js ist noch nicht installiert.", file=sys.stderr)
        print("Einmalig mit Internetverbindung ausführen: python tools/fetch_reveal.py", file=sys.stderr)
        return 2

    build = subprocess.run(
        [sys.executable, str(TOOLS / "build_catalog.py")],
        cwd=ROOT,
        check=False,
    )
    if build.returncode != 0:
        return build.returncode

    server = ThreadingHTTPServer((args.host, args.port), LocalHandler)
    print("\nPräsentationsbibliothek läuft lokal.")
    print(f"Adresse: http://{args.host}:{args.port}")
    print("Nur auf diesem Rechner erreichbar. Beenden mit Ctrl+C.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer wird beendet.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
