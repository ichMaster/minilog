"""EPUB source handler via ebooklib + beautifulsoup4."""

import re
import shutil
from pathlib import Path

from minilog.extract.converters import ConversionResult
from minilog.extract.errors import DownloadError


def _slugify_filename(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug[:80]


def convert_epub(path: Path, target_dir: Path) -> ConversionResult:
    """Convert an EPUB file to Markdown."""
    if not path.exists():
        raise DownloadError(str(path), "file not found")

    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
    except ImportError as e:
        raise DownloadError(str(path), f"ebooklib/beautifulsoup4 not installed: {e}")

    slug = _slugify_filename(path.stem)
    epub_dest = target_dir / f"{slug}.epub"
    shutil.copy2(path, epub_dest)

    try:
        book = epub.read_epub(str(path))
    except Exception as e:
        raise DownloadError(str(path), f"EPUB parsing failed: {e}")

    chapters = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), "html.parser")
        text = soup.get_text(separator="\n").strip()
        if text:
            chapters.append(text)

    if not chapters:
        raise DownloadError(str(path), "EPUB conversion produced no content")

    markdown = "\n\n---\n\n".join(chapters)
    md_path = target_dir / f"{slug}.md"
    md_path.write_text(markdown, encoding="utf-8")

    title = None
    author = None
    language = None
    try:
        title_meta = book.get_metadata("DC", "title")
        if title_meta:
            title = title_meta[0][0]
        creator_meta = book.get_metadata("DC", "creator")
        if creator_meta:
            author = creator_meta[0][0]
        lang_meta = book.get_metadata("DC", "language")
        if lang_meta:
            language = lang_meta[0][0]
    except Exception:
        pass

    return ConversionResult(
        original_path=epub_dest, markdown_path=md_path,
        title=title, author=author, language=language,
    )
