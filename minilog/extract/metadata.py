"""Write metadata.txt for a book folder."""

from datetime import datetime, timezone
from pathlib import Path

from minilog.extract.converters import ConversionResult


def write_metadata(
    target_dir: Path,
    name: str,
    results: list[ConversionResult],
    title_override: str | None = None,
    author_override: str | None = None,
    language_override: str | None = None,
) -> Path:
    """Write metadata.txt with auto-detected or overridden values."""
    # Auto-detect from first result that provides a value
    title = title_override
    author = author_override
    language = language_override

    if not title:
        for r in results:
            if r.title:
                title = r.title
                break
    if not author:
        for r in results:
            if r.author:
                author = r.author
                break
    if not language:
        for r in results:
            if r.language:
                language = r.language
                break

    # Fallback language detection
    if not language:
        try:
            from langdetect import detect
            source_md = target_dir / "source.md"
            if source_md.exists():
                sample = source_md.read_text(encoding="utf-8")[:5000]
                language = detect(sample)
        except Exception:
            language = "unknown"

    sources = []
    for r in results:
        sources.append(r.source_url or str(r.original_path.name))

    lines = [
        f"name: {name}",
        f"title: {title or 'untitled'}",
        f"author: {author or 'unknown'}",
        f"sources: {', '.join(sources)}",
        f"language: {language or 'unknown'}",
        f"created_at: {datetime.now(timezone.utc).isoformat()}",
        f"model: ",
    ]

    meta_path = target_dir / "metadata.txt"
    meta_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return meta_path
