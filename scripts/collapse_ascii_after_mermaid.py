#!/usr/bin/env python3
"""Wrap legacy ASCII box diagrams in collapsible details when mermaid exists above."""

import re
from pathlib import Path

POSTS = Path(__file__).resolve().parent.parent / "_posts"
BOX = re.compile(r"[┌└│▼├─┤┬┴╔╗╚╝║═]")

BLOCK = re.compile(
    r"(<p class=\"diagram-caption\">.*?</p>\n+)"
    r"(```\n(?P<body>.*?)```)",
    re.DOTALL,
)


def wrap_ascii(match: re.Match) -> str:
    caption = match.group(1)
    body = match.group("body")
    if not BOX.search(body):
        return match.group(0)
    if "<details" in body:
        return match.group(0)
    return (
        f"{caption}"
        f'<details class="lp-collapse" markdown="1">\n'
        f"<summary>Expanded ASCII diagram (optional detail)</summary>\n\n"
        f"```\n{body}```\n\n"
        f"</details>\n\n"
    )


def process(path: Path) -> bool:
    if "Architecture at a glance" not in path.read_text(encoding="utf-8"):
        return False
    text = path.read_text(encoding="utf-8")
    new = BLOCK.sub(wrap_ascii, text, count=1)
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    n = sum(process(p) for p in POSTS.glob("*.md"))
    print(f"Collapsed ASCII in {n} posts.")


if __name__ == "__main__":
    main()
