#!/usr/bin/env python3
"""Check the generated Pages artifact covers every tracked Markdown page."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from build_docs_site import ROOT, _build_source_map, tracked_markdown_files


def expected_page(site: Path, staged: str) -> Path:
    path = Path(staged)
    if path.name == "index.md":
        return site / path.parent / "index.html"
    return site / path.with_suffix("") / "index.html"


def main() -> int:
    site = ROOT / "site"
    if not site.is_dir():
        print(f"ERROR: generated site is missing: {site}", file=sys.stderr)
        return 1

    source_map = _build_source_map(tracked_markdown_files(ROOT))
    missing = [
        f"{source} -> {expected_page(site, staged)}"
        for source, staged in source_map.items()
        if not expected_page(site, staged).is_file()
    ]
    if missing:
        for item in missing:
            print(f"ERROR: missing generated page: {item}", file=sys.stderr)
        return 1

    html_files = list(site.rglob("*.html"))
    unresolved_md_links: list[str] = []
    mermaid_blocks = 0
    for html_file in html_files:
        html = html_file.read_text(encoding="utf-8")
        mermaid_blocks += html.count('class="mermaid"')
        for href in re.findall(r'href=["\']([^"\']+)["\']', html):
            parsed = urlsplit(href)
            if parsed.netloc or parsed.scheme or not parsed.path:
                continue
            if parsed.path.endswith(".md"):
                unresolved_md_links.append(f"{html_file.relative_to(site)}: {href}")

    if unresolved_md_links:
        for item in unresolved_md_links:
            print(f"ERROR: generated site still contains Markdown link: {item}", file=sys.stderr)
        return 1

    required_assets = [
        site / "index.html",
        site / "docs/images/mivia-agent-skill.webp",
        site / "mivialabs-logo.v2.webp",
        site / "stylesheets/extra.css",
        site / "fonts/inter-latin-wght-normal.woff2",
        site / "fonts/space-grotesk-latin-500-normal.woff2",
        site / "fonts/ibm-plex-mono-latin-400-normal.woff2",
    ]
    missing_assets = [str(path.relative_to(site)) for path in required_assets if not path.is_file()]
    if missing_assets:
        print(f"ERROR: generated site is missing assets: {', '.join(missing_assets)}", file=sys.stderr)
        return 1

    social_image = (
        'https://mivialabs.github.io/mivia-agent-skills/'
        'docs/images/mivia-agent-skill.webp'
    )
    article_social_image = (
        'https://mivialabs.github.io/mivia-agent-skills/'
        'articles/engineering-working-contracts/engineering-working-contracts.webp'
    )
    missing_social_metadata = [
        html_file.relative_to(site)
        for html_file in html_files
        if not (
            (
                f'<meta property="og:image" content="{social_image}">'
                in html_file.read_text(encoding="utf-8")
            )
            or (
                f'<meta property="og:image" content="{article_social_image}">'
                in html_file.read_text(encoding="utf-8")
            )
        )
        or '<meta name="twitter:card" content="summary_large_image">' not in html_file.read_text(
            encoding="utf-8"
        )
    ]
    if missing_social_metadata:
        print(
            "ERROR: generated pages are missing default social preview metadata: "
            + ", ".join(str(path) for path in missing_social_metadata),
            file=sys.stderr,
        )
        return 1

    article_html = site / "articles/engineering-working-contracts/index.html"
    article_html_text = article_html.read_text(encoding="utf-8")
    if f'<meta property="og:image" content="{article_social_image}">' not in article_html_text:
        print("ERROR: article-specific social image was not applied", file=sys.stderr)
        return 1
    if '<meta property="og:image:alt" content="Engineering Working Contracts article splash illustration">' not in article_html_text:
        print("ERROR: article-specific social image alt text was not applied", file=sys.stderr)
        return 1
    if social_image in article_html_text:
        print("ERROR: article page still uses the default social image", file=sys.stderr)
        return 1

    source_mermaid_blocks = sum(
        (ROOT / source).read_text(encoding="utf-8").count("```mermaid")
        for source in source_map
    )
    if mermaid_blocks < source_mermaid_blocks:
        print(
            "ERROR: generated site lost Mermaid blocks: "
            f"expected at least {source_mermaid_blocks}, found {mermaid_blocks}",
            file=sys.stderr,
        )
        return 1

    print(
        "Generated site checks passed: "
        f"{len(source_map)} Markdown pages, {len(html_files)} HTML files, "
        f"{mermaid_blocks} Mermaid blocks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
