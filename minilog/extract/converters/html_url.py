"""HTML URL source handler via trafilatura."""

import re
from pathlib import Path
from urllib.parse import urlparse

from minilog.extract.converters import ConversionResult
from minilog.extract.errors import DownloadError


def _slugify_url(url: str) -> str:
    """Derive a filename slug from a URL."""
    parsed = urlparse(url)
    raw = parsed.netloc + parsed.path
    slug = re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")
    return slug[:80]


def download_html(url: str, target_dir: Path) -> ConversionResult:
    """Download a URL, extract main content via trafilatura, save as Markdown."""
    try:
        import trafilatura
    except ImportError as e:
        raise DownloadError(url, f"trafilatura not installed: {e}")

    slug = _slugify_url(url)

    # Fetch the page
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        raise DownloadError(url, "failed to fetch URL (network error or invalid URL)")

    # Save original HTML
    html_path = target_dir / f"{slug}.html"
    html_path.write_text(downloaded, encoding="utf-8")

    # Extract main content as Markdown
    markdown = trafilatura.extract(downloaded, output_format="markdown")
    if not markdown:
        raise DownloadError(url, "trafilatura could not extract any content from the page")

    md_path = target_dir / f"{slug}.md"
    md_path.write_text(markdown, encoding="utf-8")

    # Extract metadata
    metadata = trafilatura.extract_metadata(downloaded)
    title = metadata.title if metadata else None
    author = metadata.author if metadata else None
    language = None
    if metadata and hasattr(metadata, "language"):
        language = metadata.language

    return ConversionResult(
        original_path=html_path,
        markdown_path=md_path,
        title=title,
        author=author,
        language=language,
        source_url=url,
    )
