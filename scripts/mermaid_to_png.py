#!/usr/bin/env python3
"""Convert ```mermaid blocks to static PNG images for reliable display."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
DIAGRAMS_DIR = ROOT / "assets" / "diagrams"
SOURCES_DIR = ROOT / "_diagrams" / "sources"
CONFIG = ROOT / "_diagrams" / "mermaid-config.json"
PUPPETEER = ROOT / "_diagrams" / "puppeteer-config.json"
MMDC = ROOT / "node_modules" / ".bin" / "mmdc"

MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
LIQUID_RE = re.compile(r"\{\{.*?\}\}", re.DOTALL)


def preprocess_mermaid(source: str) -> str:
    """Strip Jekyll Liquid so mmdc can render (static snapshot)."""
    return LIQUID_RE.sub("172", source)

def figure_html(filename: str, alt: str) -> str:
    return (
        '<figure class="diagram-figure">\n'
        f'  <img src="{{{{ \'/assets/diagrams/{filename}\' | relative_url }}}}" '
        f'alt="{alt}" class="diagram-img" loading="lazy" />\n'
        "</figure>\n"
    )

# content hash -> png filename (deduplicate identical diagrams)
_hash_to_file: dict[str, str] = {}


def slug_from_path(path: Path) -> str:
    name = path.stem
    if name == "system-design-list":
        return "system-design-list"
    return name


def alt_for_block(source: str, index: int) -> str:
    first = source.strip().split("\n", 1)[0].strip()
    if first.startswith("sequenceDiagram"):
        return "Request flow sequence diagram"
    if first.startswith("stateDiagram"):
        return "State diagram"
    if first.startswith("gantt"):
        return "Timeline diagram"
    if first.startswith("pie"):
        return "Distribution chart"
    if "flowchart" in first or "graph" in first:
        return "System architecture diagram"
    return f"Diagram {index}"


def ensure_mmdc() -> Path:
    if MMDC.exists():
        return MMDC
    print("Installing @mermaid-js/mermaid-cli (npm install)...", file=sys.stderr)
    subprocess.run(
        ["npm", "install", "--no-save", "@mermaid-js/mermaid-cli@10.9.0"],
        cwd=ROOT,
        check=True,
    )
    if not MMDC.exists():
        raise RuntimeError("mmdc not found after npm install")
    return MMDC


def render_png(mmdc: Path, source: str, out_png: Path, force: bool) -> None:
    if out_png.exists() and not force:
        return
    out_png.parent.mkdir(parents=True, exist_ok=True)
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    content_hash = hashlib.sha256(source.encode()).hexdigest()[:16]
    mmd_path = SOURCES_DIR / f"{content_hash}.mmd"
    mmd_path.write_text(preprocess_mermaid(source).strip() + "\n", encoding="utf-8")
    cmd = [
        str(mmdc),
        "-i",
        str(mmd_path),
        "-o",
        str(out_png),
        "-b",
        "white",
        "-w",
        "1400",
        "-c",
        str(CONFIG),
        "-p",
        str(PUPPETEER),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"WARN: mmdc failed for {out_png.name}: {result.stderr[:500]}", file=sys.stderr)
        raise RuntimeError(f"mmdc failed: {out_png.name}")


def png_for_source(
    mmdc: Path,
    source: str,
    file_slug: str,
    index: int,
    force: bool,
) -> str:
    content_hash = hashlib.sha256(source.encode()).hexdigest()[:16]
    if content_hash in _hash_to_file:
        return _hash_to_file[content_hash]
    filename = f"{file_slug}-{index:02d}.png"
    # If deduping, use hash-based name for storage but keep per-post alias via symlink?
    # Use hash name for deduped content, first occurrence wins
    hash_filename = f"{content_hash}.png"
    out_png = DIAGRAMS_DIR / hash_filename
    render_png(mmdc, source, out_png, force)
    _hash_to_file[content_hash] = hash_filename
    return hash_filename


def convert_file(mmdc: Path, path: Path, force: bool, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    if "```mermaid" not in text:
        return 0
    slug = slug_from_path(path)
    count = 0
    new_parts: list[str] = []
    last = 0
    for i, match in enumerate(MERMAID_RE.finditer(text), start=1):
        source = match.group(1)
        new_parts.append(text[last : match.start()])
        try:
            png_name = png_for_source(mmdc, source, slug, i, force)
            alt = alt_for_block(source, i)
            replacement = figure_html(png_name, alt)
            if not dry_run:
                new_parts.append(replacement)
            else:
                new_parts.append(f"<!-- would be {png_name} -->\n")
            count += 1
        except RuntimeError as e:
            print(f"SKIP block {i} in {path.name}: {e}", file=sys.stderr)
            new_parts.append(match.group(0))
        last = match.end()
    new_parts.append(text[last:])
    if count and not dry_run:
        path.write_text("".join(new_parts), encoding="utf-8")
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Regenerate existing PNGs")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("files", nargs="*", help="Specific markdown files")
    args = parser.parse_args()

    mmdc = ensure_mmdc()
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)

    if args.files:
        paths = [Path(f) for f in args.files]
    else:
        paths = sorted(POSTS.glob("*.md"))
        list_page = ROOT / "system-design-list.md"
        if list_page.exists():
            paths.append(list_page)

    total_blocks = 0
    total_files = 0
    for path in paths:
        n = convert_file(mmdc, path, args.force, args.dry_run)
        if n:
            total_files += 1
            total_blocks += n
            print(f"{path.name}: {n} diagram(s)")

    print(f"\nDone. {total_blocks} diagrams in {total_files} files.")
    print(f"PNG output: {DIAGRAMS_DIR}")


if __name__ == "__main__":
    main()
