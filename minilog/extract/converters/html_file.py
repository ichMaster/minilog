"""Local HTML file handler via trafilatura."""

import re
import shutil
from pathlib import Path

from minilog.extract.converters import ConversionResult
from minilog.extract.errors import DownloadError


def _slugify_filename(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug[:80]


def convert_html_file(path: Path, target_dir: Path) -> ConversionResult:
    """Convert a local HTML file to Markdown via trafilatura."""
    if not path.exists():
        raise DownloadError(str(path), "file not found")

    try:
        import trafilatura
    except ImportError as e:
        raise DownloadError(str(path), f"trafilatura not installed: {e}")

    slug = _slugify_filename(path.stem)
    html_dest = target_dir / f"{slug}.html"
    shutil.copy2(path, html_dest)

    html_content = path.read_text(encoding="utf-8")
    markdown = trafilatura.extract(html_content, output_format="markdown")
    if not markdown:
        raise DownloadError(str(path), "trafilatura could not extract content from HTML file")

    md_path = target_dir / f"{slug}.md"
    md_path.write_text(markdown, encoding="utf-8")

    metadata = trafilatura.extract_metadata(html_content)
    title = metadata.title if metadata else None
    author = metadata.author if metadata else None

    return ConversionResult(
        original_path=html_dest, markdown_path=md_path,
        title=title, author=author,
    )
