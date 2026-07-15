#!/usr/bin/env python3
"""Check the generated Pages artifact covers every tracked Markdown page."""

from __future__ import annotations

import re
import shutil
import sys
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from build_docs_site import ROOT, _build_source_map, build_site, tracked_markdown_files


def expected_page(site: Path, staged: str) -> Path:
    path = Path(staged)
    if path.name == "index.md":
        return site / path.parent / "index.html"
    return site / path.with_suffix("") / "index.html"


def run(command: list[str], cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(f"Command failed: {' '.join(command)}\n{result.stderr}")


def docs_fixture() -> Path:
    temporary = Path(tempfile.mkdtemp(prefix="mivia-docs-render-"))
    shutil.copytree(
        ROOT,
        temporary,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".git", ".docs-staging", "site", "dist", "__pycache__"),
    )
    run(["git", "init", "--quiet"], temporary)
    run(["git", "config", "user.email", "docs@example.com"], temporary)
    run(["git", "config", "user.name", "Docs Test"], temporary)
    run(["git", "add", "-A"], temporary)
    return temporary


def local_html_target(site: Path, html_file: Path, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    if parsed.path.startswith("#"):
        return None
    site_prefix = "/mivia-agent-skills/"
    if parsed.path.startswith("/"):
        if not parsed.path.startswith(site_prefix):
            return None
        target = (site / parsed.path[len(site_prefix) :]).resolve()
    else:
        target = (html_file.parent / parsed.path).resolve()
    if parsed.path.endswith("/"):
        target = target / "index.html"
    elif target.suffix == "":
        target = target / "index.html"
    return target


def test_docs_build_renders_and_links_every_example() -> None:
    fixture = docs_fixture()
    try:
        tracked = tracked_markdown_files(fixture)
        expected_sources = [
            Path("skills") / skill / "references" / "examples" / filename
            for skill, filenames in {
                "engineering-working-contract": (
                    "01-concurrency-fix.md",
                    "02-production-containment.md",
                ),
                "verify-code-change": (
                    "01-parser-regression-pass.md",
                    "02-database-migration-partial.md",
                ),
                "deep-bug-audit": (
                    "01-current-session-cross-boundary.md",
                    "02-targeted-auth-persistence-audit.md",
                ),
                "mivia-image-generation": (
                    "01-readme-banner.md",
                    "02-image-capability-unavailable.md",
                ),
            }.items()
            for filename in filenames
        ]
        assert all(source in tracked for source in expected_sources)

        mkdocs = shutil.which("mkdocs")
        if mkdocs is None:
            raise AssertionError("MkDocs is required for generated example-link verification")
        site = fixture / "rendered-site"
        assert build_site(fixture, site_dir=site, mkdocs_command=mkdocs) == 0
        source_map = _build_source_map(tracked)

        expected_pages = [
            expected_page(site, source_map[source.as_posix()]) for source in expected_sources
        ]
        assert all(page.is_file() for page in expected_pages)

        public_index = expected_page(site, source_map["docs/examples.md"])
        public_html = public_index.read_text(encoding="utf-8")
        public_targets = {
            target
            for href in re.findall(r'href=["\']([^"\']+)["\']', public_html)
            if (target := local_html_target(site, public_index, href)) is not None
        }
        assert all(page in public_targets for page in expected_pages)

        example_index = {
            "engineering-working-contract": (
                "01-concurrency-fix.md",
                "02-production-containment.md",
            ),
            "verify-code-change": (
                "01-parser-regression-pass.md",
                "02-database-migration-partial.md",
            ),
            "deep-bug-audit": (
                "01-current-session-cross-boundary.md",
                "02-targeted-auth-persistence-audit.md",
            ),
            "mivia-image-generation": (
                "01-readme-banner.md",
                "02-image-capability-unavailable.md",
            ),
        }
        for skill, filenames in example_index.items():
            skill_source = (Path("skills") / skill / "SKILL.md").as_posix()
            skill_page = expected_page(site, source_map[skill_source])
            skill_html = skill_page.read_text(encoding="utf-8")
            expected_skill_pages = [
                expected_page(
                    site,
                    source_map[
                        (
                            Path("skills")
                            / skill
                            / "references"
                            / "examples"
                            / filename
                        ).as_posix()
                    ],
                )
                for filename in filenames
            ]
            if skill == "engineering-working-contract":
                assert all(filename in skill_html for filename in filenames)
            else:
                skill_targets = {
                    target
                    for href in re.findall(r'href=["\']([^"\']+)["\']', skill_html)
                    if (target := local_html_target(site, skill_page, href)) is not None
                }
                assert all(page in skill_targets for page in expected_skill_pages)

        unresolved = []
        for html_file in site.rglob("*.html"):
            html = html_file.read_text(encoding="utf-8")
            for href in re.findall(r'href=["\']([^"\']+)["\']', html):
                target = local_html_target(site, html_file, href)
                if target is not None and not target.is_file():
                    unresolved.append(f"{html_file.relative_to(site)}: {href}")
        assert not unresolved, unresolved
    finally:
        shutil.rmtree(fixture)


def main() -> int:
    test_docs_build_renders_and_links_every_example()
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
    if (
        '<img alt="Engineering Working Contracts article splash illustration" '
        'src="engineering-working-contracts.webp" />'
        not in article_html_text
    ):
        print("ERROR: article splash image was not rendered at the top of the article", file=sys.stderr)
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
