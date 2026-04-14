"""DOCX source handler via python-docx."""

import re
import shutil
from pathlib import Path

from minilog.extract.converters import ConversionResult
from minilog.extract.errors import DownloadError


def _slugify_filename(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug[:80]


def convert_docx(path: Path, target_dir: Path) -> ConversionResult:
    """Convert a DOCX file to Markdown."""
    if not path.exists():
        raise DownloadError(str(path), "file not found")

    try:
        import docx
    except ImportError as e:
        raise DownloadError(str(path), f"python-docx not installed: {e}")

    slug = _slugify_filename(path.stem)
    docx_dest = target_dir / f"{slug}.docx"
    shutil.copy2(path, docx_dest)

    try:
        doc = docx.Document(str(path))
    except Exception as e:
        raise DownloadError(str(path), f"DOCX parsing failed: {e}")

    lines = []
    for para in doc.paragraphs:
        style = para.style.name if para.style else ""
        text = para.text.strip()
        if not text:
            lines.append("")
            continue
        if "Heading 1" in style:
            lines.append(f"# {text}")
        elif "Heading 2" in style:
            lines.append(f"## {text}")
        elif "Heading 3" in style:
            lines.append(f"### {text}")
        else:
            lines.append(text)
        lines.append("")

    markdown = "\n".join(lines)
    md_path = target_dir / f"{slug}.md"
    md_path.write_text(markdown, encoding="utf-8")

    title = doc.core_properties.title if doc.core_properties.title else None
    author = doc.core_properties.author if doc.core_properties.author else None

    return ConversionResult(
        original_path=docx_dest, markdown_path=md_path,
        title=title, author=author,
    )
