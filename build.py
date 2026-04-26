#!/usr/bin/env python3
"""
Ingenious Services Static Site Builder
--------------------------------------
Reads page content from pages/ and wraps each page with
the shared header and footer partials from partials/.

Output goes to dist/ — ready to deploy on Cloudflare Pages.

Usage:
    python3 build.py
"""

import json
import re
import shutil
from pathlib import Path

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
ROOT = Path(__file__).parent
PARTIALS = ROOT / "partials"
PAGES = ROOT / "pages"
ASSETS_SRC = ROOT / "assets"
DIST = ROOT / "dist"

# ──────────────────────────────────────────────
# Load partials
# ──────────────────────────────────────────────
HEAD_TEMPLATE = (PARTIALS / "head.html").read_text()
HEADER_EN = (PARTIALS / "header.html").read_text()
FOOTER_EN = (PARTIALS / "footer.html").read_text()
HEADER_ES = (PARTIALS / "header-es.html").read_text()
FOOTER_ES = (PARTIALS / "footer-es.html").read_text()

# ──────────────────────────────────────────────
# Load manifest
# ──────────────────────────────────────────────
manifest = json.loads((PAGES / "manifest.json").read_text())


def build_page(page: dict) -> str:
    """Assemble a complete HTML page from partials + content."""
    lang = page.get("lang", "en")
    title = page.get("title", "Ingenious Services")
    desc = page.get("description", "")
    canonical = page.get("canonical", "")
    source_rel = page.get("source", "")

    # Read page body content
    source_path = ROOT / source_rel
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source_path}")
    body_content = source_path.read_text()

    # Build <head>
    head = HEAD_TEMPLATE
    head = head.replace("{{LANG}}", lang)
    head = head.replace("{{TITLE}}", title)
    head = head.replace("{{DESCRIPTION}}", desc)
    head = head.replace("{{CANONICAL}}", canonical)

    # Pick correct EN/ES header and footer
    if lang == "es":
        header = HEADER_ES
        footer = FOOTER_ES
    else:
        header = HEADER_EN
        footer = FOOTER_EN

    return f"{head}\n{header}\n{body_content}\n{footer}\n</body></html>"


def build_all():
    # Clean and recreate dist
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    # Copy assets (CSS, JS, images, etc.)
    if ASSETS_SRC.exists():
        shutil.copytree(ASSETS_SRC, DIST / "assets")
        print(f"  ✓ Copied assets/")

    # Copy static root files
    for static_file in ROOT.glob("static/*"):
        dest = DIST / static_file.name
        shutil.copy2(static_file, dest)
        print(f"  ✓ Copied static/{static_file.name}")

    # Build each page
    built = 0
    errors = 0
    for page in manifest:
        path = page["path"]
        try:
            html = build_page(page)

            # Determine output path
            if path == "/":
                out_file = DIST / "index.html"
            else:
                clean = path.lstrip("/")
                out_file = DIST / clean / "index.html"

            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(html)
            built += 1
        except Exception as e:
            print(f"  ✗ ERROR building {path}: {e}")
            errors += 1

    print(f"\nBuild complete: {built} pages built, {errors} errors → dist/")


if __name__ == "__main__":
    print("Building Ingenious Services static site...")
    build_all()
