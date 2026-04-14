"""Merge multiple source conversions into a single source.md."""

from pathlib import Path

from minilog.extract.converters import ConversionResult


def merge_sources(results: list[ConversionResult], target_dir: Path) -> Path:
    """Merge all converted Markdown files into source.md with separators."""
    parts = []
    for result in results:
        source_id = result.source_url or result.original_path.name
        header = f"% Source: {source_id}"
        content = result.markdown_path.read_text(encoding="utf-8")
        parts.append(f"{header}\n\n{content}")

    merged = "\n\n---\n\n".join(parts)
    source_path = target_dir / f"{target_dir.name}.md"
    source_path.write_text(merged, encoding="utf-8")
    return source_path
