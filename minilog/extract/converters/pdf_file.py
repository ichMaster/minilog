"""PDF source handler via pymupdf4llm."""

import re
import shutil
from pathlib import Path

from minilog.extract.converters import ConversionResult
from minilog.extract.errors import DownloadError


def _slugify_filename(name: str) -> str:
    """Derive a slug from a filename (without extension)."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug[:80]


def convert_pdf(path: Path, target_dir: Path) -> ConversionResult:
    """Convert a PDF file to Markdown via pymupdf4llm."""
    if not path.exists():
        raise DownloadError(str(path), "file not found")

    try:
        import pymupdf4llm
    except ImportError as e:
        raise DownloadError(str(path), f"pymupdf4llm not installed: {e}")

    slug = _slugify_filename(path.stem)

    # Copy original
    pdf_dest = target_dir / f"{slug}.pdf"
    shutil.copy2(path, pdf_dest)

    # Convert to Markdown
    try:
        markdown = pymupdf4llm.to_markdown(str(path))
    except Exception as e:
        raise DownloadError(str(path), f"PDF conversion failed: {e}")

    if not markdown or not markdown.strip():
        raise DownloadError(str(path), "PDF conversion produced empty output")

    md_path = target_dir / f"{slug}.md"
    md_path.write_text(markdown, encoding="utf-8")

    # Try to extract metadata from PDF
    title = None
    author = None
    try:
        import pymupdf
        doc = pymupdf.open(str(path))
        meta = doc.metadata
        if meta:
            title = meta.get("title") or None
            author = meta.get("author") or None
        doc.close()
    except Exception:
        pass

    return ConversionResult(
        original_path=pdf_dest,
        markdown_path=md_path,
        title=title,
        author=author,
    )
