#!/usr/bin/env python3
"""Remove auto-inserted diagrams from non-design-problem posts."""

import re
from pathlib import Path

POSTS = Path(__file__).resolve().parent.parent / "_posts"

EXCLUDE = re.compile(
    r"questions|references|learning-path|trade-offs|common-domain|common-non-distributed|"
    r"common-technologies|leetcode-practice|prep-todo|prep-guide|drill|breakdown|"
    r"vs-product|scenarios|in-domain-design|specswe|interview-framework|"
    r"interview-guide|system-design-interview\.md|os-frameworks-system-design\.md|"
    r"os-frameworks-design-interview|os-frameworks-domain|distributed-system-design-ecosystem|"
    r"android-os-design-overview|overview-cloud|overview-embedded",
    re.I,
)

MARKER_START = "### Architecture at a glance"
READING_TIP = re.compile(
    r'<div class="post-reading-tip" markdown="1">.*?</div>\s*',
    re.DOTALL,
)
HLD_BLOCK = re.compile(
    r"\n## High-Level Design\n\n### Architecture at a glance\n\n```mermaid.*?```\n\n<p class=\"diagram-caption\">.*?</p>\n\n",
    re.DOTALL,
)


def cleanup(path: Path) -> bool:
    if not EXCLUDE.search(path.name):
        return False
    text = path.read_text(encoding="utf-8")
    original = text
    text = READING_TIP.sub("", text)
    text = HLD_BLOCK.sub("", text)
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    n = sum(cleanup(p) for p in POSTS.glob("*.md"))
    print(f"Cleaned {n} files.")


if __name__ == "__main__":
    main()
