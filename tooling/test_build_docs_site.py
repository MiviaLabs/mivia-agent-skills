#!/usr/bin/env python3
"""Exercise tracked-Markdown staging and MkDocs command handling."""

from __future__ import annotations

import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

from build_docs_site import (
    STAGING_MARKER,
    STAGING_NAME,
    build_site,
    stage_site,
    stage_markdown_files,
    staged_docs,
)


def run(command: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise AssertionError(f"Command failed: {' '.join(command)}\n{result.stderr}")
    return result


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git_repository() -> Path:
    temporary = Path(tempfile.mkdtemp(prefix="mivia-docs-test-"))
    run(["git", "init", "--quiet"], temporary)
    run(["git", "config", "user.email", "test@example.com"], temporary)
    run(["git", "config", "user.name", "Docs Test"], temporary)
    return temporary


def test_staging_maps_markdown_and_preserves_links() -> None:
    root = git_repository()
    try:
        write(
            root / "README.md",
            """# Root

[Article](articles/README.md#section)
[Guide](docs/guide.markdown)
[External](https://example.com/README.md)
[Code](README.md)

```text
[Do not rewrite](articles/README.md)
```
""",
        )
        write(root / "articles/README.md", "# Article\n\n[Root](../README.md)\n")
        write(root / "docs/guide.markdown", "# Guide\n")
        write(root / "untracked.md", "# Not staged\n")
        run(["git", "add", "README.md", "articles/README.md", "docs/guide.markdown"], root)

        staging = root / "staging"
        source_map = stage_markdown_files(root, staging)

        assert source_map == {
            "README.md": "index.md",
            "articles/README.md": "articles/index.md",
            "docs/guide.markdown": "docs/guide.md",
        }
        assert (staging / "index.md").read_text(encoding="utf-8") == """# Root

[Article](articles/index.md#section)
[Guide](docs/guide.md)
[External](https://example.com/README.md)
[Code](index.md)

```text
[Do not rewrite](articles/README.md)
```
"""
        assert (staging / "articles/index.md").read_text(encoding="utf-8") == (
            "# Article\n\n[Root](../index.md)\n"
        )
        assert not (staging / "untracked.md").exists()
    finally:
        if root.exists():
            shutil.rmtree(root)


def test_staging_rejects_destination_collisions() -> None:
    root = git_repository()
    try:
        write(root / "README.md", "# Root\n")
        write(root / "index.md", "# Existing index\n")
        run(["git", "add", "README.md", "index.md"], root)
        try:
            stage_markdown_files(root, root / "staging")
        except RuntimeError as exc:
            assert "staging collision" in str(exc)
        else:
            raise AssertionError("README.md and index.md were allowed to collide")
    finally:
        shutil.rmtree(root)


def test_staging_context_cleans_generated_files() -> None:
    root = git_repository()
    try:
        write(root / "README.md", "# Root\n")
        run(["git", "add", "README.md"], root)
        with staged_docs(root) as (staging, _):
            assert (staging / "index.md").exists()
            assert (staging / STAGING_MARKER).exists()
        assert not (root / STAGING_NAME).exists()
    finally:
        shutil.rmtree(root)


def test_staging_copies_static_site_assets() -> None:
    root = git_repository()
    try:
        write(root / "README.md", "# Root\n")
        write(root / "docs-site/stylesheets/extra.css", "body { color: red; }\n")
        write(root / "docs/images/example.webp", "image bytes\n")
        run(["git", "add", "README.md"], root)
        staging = root / "staging"
        stage_markdown_files(root, staging)
        assert (staging / "stylesheets/extra.css").read_text(encoding="utf-8") == (
            "body { color: red; }\n"
        )
        assert (staging / "docs/images/example.webp").read_text(encoding="utf-8") == (
            "image bytes\n"
        )
    finally:
        shutil.rmtree(root)


def test_stage_site_leaves_files_for_mkdocs() -> None:
    root = git_repository()
    try:
        write(root / "README.md", "# Root\n")
        write(root / "mkdocs.yml", "site_name: Test\n")
        run(["git", "add", "README.md", "mkdocs.yml"], root)

        assert stage_site(root) == 0
        assert (root / STAGING_NAME / "index.md").is_file()
        assert (root / STAGING_NAME / STAGING_MARKER).is_file()
    finally:
        shutil.rmtree(root)


def test_build_site_invokes_command_and_cleans_staging() -> None:
    root = git_repository()
    try:
        write(root / "README.md", "# Root\n")
        write(
            root / "mkdocs.yml",
            "site_name: Test\ndocs_dir: .docs-staging\nsite_dir: site\n",
        )
        run(["git", "add", "README.md", "mkdocs.yml"], root)

        fake_mkdocs = root / "fake-mkdocs"
        write(
            fake_mkdocs,
            """#!/usr/bin/env python3
from pathlib import Path
assert (Path('.docs-staging') / 'index.md').is_file()
Path('called').write_text('ok', encoding='utf-8')
""",
        )
        fake_mkdocs.chmod(fake_mkdocs.stat().st_mode | stat.S_IXUSR)
        site_dir = root / "output"

        assert build_site(root, site_dir=site_dir, mkdocs_command=str(fake_mkdocs)) == 0
        assert (root / "called").read_text(encoding="utf-8") == "ok"
        assert not (root / STAGING_NAME).exists()
    finally:
        shutil.rmtree(root)


def main() -> int:
    test_staging_maps_markdown_and_preserves_links()
    test_staging_rejects_destination_collisions()
    test_staging_context_cleans_generated_files()
    test_staging_copies_static_site_assets()
    test_stage_site_leaves_files_for_mkdocs()
    test_build_site_invokes_command_and_cleans_staging()
    print("Docs build staging tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
