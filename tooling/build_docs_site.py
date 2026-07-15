#!/usr/bin/env python3
"""Stage tracked Markdown files and build the MkDocs site."""

from __future__ import annotations

import argparse
import os
import posixpath
import re
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from urllib.parse import quote, unquote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
STAGING_NAME = ".docs-staging"
STAGING_MARKER = ".mivia-agent-skills-staging"
STATIC_ASSET_SOURCES = (
    (Path("docs-site"), Path(".")),
)
MARKDOWN_SUFFIXES = {".md", ".markdown"}
IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
IMAGE_SUFFIX_PRIORITY = (".webp", ".png", ".jpg", ".jpeg", ".avif", ".gif")
DEFAULT_SOCIAL_IMAGE_PATH = "docs/images/mivia-agent-skill.webp"

INLINE_LINK = re.compile(
    r"(?P<prefix>!?\[[^\]]*\]\()"
    r"(?P<destination><[^>\n]+>|[^)\s]+)"
    r"(?P<suffix>[^)\n]*\))"
)
FENCE = re.compile(r"^[ \t]{0,3}(?P<marker>`{3,}|~{3,})")


def _as_posix(path: Path) -> str:
    return path.as_posix()


def _is_markdown(path: Path) -> bool:
    return path.suffix.casefold() in MARKDOWN_SUFFIXES


def _staged_relative_path(source: Path) -> Path:
    if source.name.casefold() in {"readme.md", "readme.markdown"}:
        return source.with_name("index.md")
    if source.suffix.casefold() != ".md":
        return source.with_suffix(".md")
    return source


def tracked_markdown_files(root: Path) -> list[Path]:
    """Return tracked Markdown paths relative to *root*, in stable order."""

    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Git is required to identify tracked Markdown files") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode(errors="replace").strip()
        message = "Unable to list tracked files with Git"
        if detail:
            message += f": {detail}"
        raise RuntimeError(message) from exc

    paths = [
        Path(os.fsdecode(raw))
        for raw in result.stdout.split(b"\0")
        if raw and _is_markdown(Path(os.fsdecode(raw)))
    ]
    return sorted(paths, key=_as_posix)


def _relative_source_path(root: Path, relative: Path) -> Path:
    source = root / relative
    try:
        resolved = source.resolve(strict=True)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Tracked Markdown file is missing: {relative}") from exc
    if not resolved.is_file():
        raise RuntimeError(f"Tracked Markdown path is not a file: {relative}")
    if not resolved.is_relative_to(root.resolve()):
        raise RuntimeError(f"Tracked Markdown path resolves outside the repository: {relative}")
    return source


def _build_source_map(files: list[Path]) -> dict[str, str]:
    source_map: dict[str, str] = {}
    destinations: dict[str, str] = {}
    for source in files:
        source_key = _as_posix(source)
        destination_key = _as_posix(_staged_relative_path(source))
        previous = destinations.get(destination_key)
        if previous is not None:
            raise RuntimeError(
                "Markdown staging collision: "
                f"{previous} and {source_key} both map to {destination_key}"
            )
        destinations[destination_key] = source_key
        source_map[source_key] = destination_key
    return source_map


def _mapped_link_destination(
    raw_destination: str,
    source: Path,
    source_map: dict[str, str],
    directory_map: dict[str, str],
) -> str:
    angle_wrapped = raw_destination.startswith("<") and raw_destination.endswith(">")
    destination = raw_destination[1:-1] if angle_wrapped else raw_destination
    parsed = urlsplit(destination)
    if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
        return raw_destination

    source_path = source.parent.as_posix()
    target_path = unquote(parsed.path)
    normalized_target = posixpath.normpath(posixpath.join(source_path, target_path))
    if normalized_target == "." or normalized_target.startswith("../"):
        return raw_destination

    staged_target = source_map.get(normalized_target)
    if staged_target is None:
        staged_target = directory_map.get(normalized_target)
    if staged_target is None:
        return raw_destination

    staged_source = source_map[_as_posix(source)]
    staged_parent = posixpath.dirname(staged_source) or "."
    relative_target = posixpath.relpath(staged_target, staged_parent)
    relative_target = quote(relative_target, safe="/._-~")
    rewritten = urlunsplit(("", "", relative_target, parsed.query, parsed.fragment))
    return f"<{rewritten}>" if angle_wrapped else rewritten


def rewrite_internal_links(
    text: str,
    source: Path,
    source_map: dict[str, str],
    directory_map: dict[str, str],
) -> str:
    """Rewrite links to staged Markdown paths, leaving code fences untouched."""

    output: list[str] = []
    in_fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        fence_match = FENCE.match(line)
        if in_fence is not None:
            output.append(line)
            if (
                fence_match is not None
                and fence_match.group("marker")[0] == in_fence[0]
                and len(fence_match.group("marker")) >= in_fence[1]
            ):
                in_fence = None
            continue

        if fence_match is not None:
            in_fence = (
                fence_match.group("marker")[0],
                len(fence_match.group("marker")),
            )
            output.append(line)
            continue

        def replace(match: re.Match[str]) -> str:
            prefix = match.group("prefix")
            if prefix.startswith("!"):
                return match.group(0)
            destination = _mapped_link_destination(
                match.group("destination"), source, source_map, directory_map
            )
            return f"{prefix}{destination}{match.group('suffix')}"

        output.append(INLINE_LINK.sub(replace, line))
    return "".join(output)


def _directory_map(source_map: dict[str, str]) -> dict[str, str]:
    destinations = set(source_map.values())
    directories: set[str] = set()
    for destination in destinations:
        path = Path(destination).parent
        while True:
            directory = _as_posix(path)
            directories.add("" if directory == "." else directory)
            if path == Path("."):
                break
            path = path.parent

    result: dict[str, str] = {}
    for directory in sorted(directories):
        candidate = "index.md" if not directory else f"{directory}/index.md"
        result[directory] = candidate
    return result


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _display_name(path: str) -> str:
    return path.replace("-", " ").replace("_", " ").title()


def _generated_directory_index(
    directory: str, source_map: dict[str, str], root: Path
) -> str:
    prefix = f"{directory}/" if directory else ""
    direct_files: list[tuple[str, str]] = []
    child_directories: set[str] = set()
    for source, staged in source_map.items():
        if not staged.startswith(prefix):
            continue
        remainder = staged[len(prefix) :]
        if "/" in remainder:
            child_directories.add(remainder.split("/", 1)[0])
            continue
        if remainder == "index.md":
            continue
        title = _title((root / source).read_text(encoding="utf-8"), remainder[:-3])
        direct_files.append((remainder, title))

    lines = [f"# {_display_name(Path(directory).name) if directory else 'Documentation'}", ""]
    if direct_files:
        lines.extend(["## Pages", ""])
        for filename, title in sorted(direct_files):
            lines.append(f"- [{title}]({filename})")
        lines.append("")
    if child_directories:
        lines.extend(["## Sections", ""])
        for child in sorted(child_directories):
            lines.append(f"- [{_display_name(child)}]({child}/index.md)")
        lines.append("")
    return "\n".join(lines)


def _stage_static_assets(root: Path, staging_dir: Path) -> None:
    for source_root, destination_root in STATIC_ASSET_SOURCES:
        assets_dir = root / source_root
        if not assets_dir.is_dir():
            continue
        for source in sorted(assets_dir.rglob("*")):
            if not source.is_file():
                continue
            if source.is_symlink():
                raise RuntimeError(f"Static documentation asset must not be a symlink: {source}")
            relative = source.relative_to(assets_dir)
            destination = staging_dir / destination_root / relative
            if destination.exists():
                collision = destination.relative_to(staging_dir)
                raise RuntimeError(
                    f"Static documentation asset collides with staged file: {collision}"
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def _stage_repository_images(root: Path, staging_dir: Path) -> None:
    """Copy repository image assets while excluding generated and theme files."""

    excluded_roots = {".git", STAGING_NAME, "site", "docs-site"}
    for source in sorted(root.rglob("*")):
        if not source.is_file() or source.suffix.casefold() not in IMAGE_SUFFIXES:
            continue
        if source.is_symlink():
            raise RuntimeError(f"Repository image asset must not be a symlink: {source}")
        relative = source.relative_to(root)
        if relative.parts and relative.parts[0] in excluded_roots:
            continue
        destination = staging_dir / relative
        if destination.exists():
            collision = destination.relative_to(staging_dir)
            raise RuntimeError(f"Repository image asset collides with staged file: {collision}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _matching_directory_image(root: Path, source: Path) -> Path | None:
    """Find the preferred image named after the Markdown file's directory."""

    directory = root / source.parent
    stem = directory.name
    if not stem:
        return None
    for suffix in IMAGE_SUFFIX_PRIORITY:
        candidate = directory / f"{stem}{suffix}"
        if candidate.is_file() and not candidate.is_symlink():
            return candidate
    return None


def _generated_html_path(site_dir: Path, staged: str) -> Path:
    path = Path(staged)
    if path.name == "index.md":
        return site_dir / path.parent / "index.html"
    return site_dir / path.with_suffix("") / "index.html"


def _apply_page_social_images(
    root: Path, site_dir: Path, source_map: dict[str, str]
) -> int:
    """Replace the default social image when a page has a directory-named image."""

    applied = 0
    image_pattern = re.compile(r'(<meta property="og:image" content=")([^"]+)(">)')
    image_alt_pattern = re.compile(r'(<meta property="og:image:alt" content=")[^"]+(">)')
    for source_key, staged in source_map.items():
        image = _matching_directory_image(root, Path(source_key))
        if image is None:
            continue
        html_path = _generated_html_path(site_dir, staged)
        if not html_path.is_file():
            continue
        html = html_path.read_text(encoding="utf-8")
        match = image_pattern.search(html)
        if match is None or not match.group(2).endswith(DEFAULT_SOCIAL_IMAGE_PATH):
            continue
        custom_path = image.relative_to(root).as_posix()
        custom_url = match.group(2)[: -len(DEFAULT_SOCIAL_IMAGE_PATH)] + custom_path
        html = html.replace(match.group(2), custom_url)
        custom_alt = f"{_display_name(image.parent.name)} article splash illustration"
        html = image_alt_pattern.sub(
            lambda alt_match: f"{alt_match.group(1)}{custom_alt}{alt_match.group(2)}",
            html,
            count=1,
        )
        html_path.write_text(html, encoding="utf-8")
        applied += 1
    return applied


def stage_markdown_files(root: Path, staging_dir: Path) -> dict[str, str]:
    """Copy tracked Markdown into *staging_dir* and return source-to-stage mappings."""

    files = tracked_markdown_files(root)
    if not files:
        raise RuntimeError("No tracked Markdown files were found")
    source_map = _build_source_map(files)
    directory_map = _directory_map(source_map)

    if staging_dir.exists() or staging_dir.is_symlink():
        if not staging_dir.is_dir() or not (staging_dir / STAGING_MARKER).is_file():
            raise RuntimeError(
                f"Refusing to use existing non-generated staging directory: {staging_dir}"
            )
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True)
    (staging_dir / STAGING_MARKER).write_text(
        "Generated by tooling/build_docs_site.py\n", encoding="utf-8"
    )
    _stage_static_assets(root, staging_dir)
    _stage_repository_images(root, staging_dir)

    for source in files:
        source_path = _relative_source_path(root, source)
        destination = staging_dir / _staged_relative_path(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = source_path.read_bytes().decode("utf-8")
        rewritten = rewrite_internal_links(text, source, source_map, directory_map)
        destination.write_bytes(rewritten.encode("utf-8"))

    source_destinations = set(source_map.values())
    for directory, destination_key in directory_map.items():
        if destination_key in source_destinations:
            continue
        destination = staging_dir / destination_key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            _generated_directory_index(directory, source_map, root), encoding="utf-8"
        )
    return source_map


def remove_generated_staging(root: Path) -> None:
    staging_dir = root / STAGING_NAME
    if not (staging_dir.exists() or staging_dir.is_symlink()):
        return
    if staging_dir.is_symlink() or not (staging_dir / STAGING_MARKER).is_file():
        raise RuntimeError(
            f"Refusing to remove non-generated staging directory: {staging_dir}"
        )
    shutil.rmtree(staging_dir)


@contextmanager
def staged_docs(root: Path) -> Iterator[tuple[Path, dict[str, str]]]:
    """Create generated staging files and always remove them after the build."""

    staging_dir = root / STAGING_NAME
    try:
        source_map = stage_markdown_files(root, staging_dir)
        yield staging_dir, source_map
    finally:
        remove_generated_staging(root)


def stage_site(root: Path) -> int:
    """Stage tracked Markdown for a separate MkDocs invocation."""

    config_file = root / "mkdocs.yml"
    if not config_file.is_file():
        raise RuntimeError(f"MkDocs configuration is missing: {config_file}")
    try:
        source_map = stage_markdown_files(root, root / STAGING_NAME)
    except Exception:
        remove_generated_staging(root)
        raise
    print(f"Staged {len(source_map)} tracked Markdown files in {STAGING_NAME}")
    return 0


def build_site(
    root: Path, *, site_dir: Path | None = None, mkdocs_command: str = "mkdocs"
) -> int:
    """Stage the repository and invoke MkDocs from the repository root."""

    config_file = root / "mkdocs.yml"
    if not config_file.is_file():
        raise RuntimeError(f"MkDocs configuration is missing: {config_file}")

    command = [mkdocs_command, "build", "--config-file", str(config_file), "--clean", "--strict"]
    if site_dir is not None:
        command.extend(["--site-dir", str(site_dir)])

    with staged_docs(root) as (_, source_map):
        try:
            result = subprocess.run(command, cwd=root)
        except FileNotFoundError as exc:
            raise RuntimeError(
                "MkDocs is required to build the site; install requirements/docs.txt first"
            ) from exc
        if result.returncode != 0:
            raise RuntimeError(f"MkDocs build failed with exit code {result.returncode}")
        output_dir = site_dir or root / "site"
        custom_images = _apply_page_social_images(root, output_dir, source_map)
        print(f"Built MkDocs site from {len(source_map)} tracked Markdown files")
        if custom_images:
            print(f"Applied {custom_images} page-specific social image(s)")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root (default: this script's repository)",
    )
    parser.add_argument(
        "--site-dir",
        type=Path,
        help="MkDocs output directory (default: the site_dir in mkdocs.yml)",
    )
    parser.add_argument(
        "--mkdocs-command",
        default="mkdocs",
        help="MkDocs executable (default: mkdocs)",
    )
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="stage files without invoking MkDocs",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    site_dir = args.site_dir
    if site_dir is not None and not site_dir.is_absolute():
        site_dir = root / site_dir
    try:
        if args.stage_only:
            return stage_site(root)
        return build_site(root, site_dir=site_dir, mkdocs_command=args.mkdocs_command)
    except (RuntimeError, UnicodeDecodeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
