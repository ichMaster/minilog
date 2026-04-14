"""Plain text and Markdown file handlers."""

import re
import shutil
from pathlib import Path

from minilog.extract.converters import ConversionResult
from minilog.extract.errors import DownloadError


def _slugify_filename(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug[:80]


def convert_txt(path: Path, target_dir: Path) -> ConversionResult:
    """Convert a plain text file (minimal processing)."""
    if not path.exists():
        raise DownloadError(str(path), "file not found")

    slug = _slugify_filename(path.stem)
    txt_dest = target_dir / f"{slug}.txt"
    shutil.copy2(path, txt_dest)

    content = path.read_text(encoding="utf-8")
    md_path = target_dir / f"{slug}.md"
    md_path.write_text(content, encoding="utf-8")

    return ConversionResult(original_path=txt_dest, markdown_path=md_path)


def convert_md(path: Path, target_dir: Path) -> ConversionResult:
    """Copy a Markdown file (already in target format)."""
    if not path.exists():
        raise DownloadError(str(path), "file not found")

    slug = _slugify_filename(path.stem)
    md_dest = target_dir / f"{slug}.md"
    shutil.copy2(path, md_dest)

    return ConversionResult(original_path=md_dest, markdown_path=md_dest)
