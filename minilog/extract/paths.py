"""Path helpers for the extraction workflow."""

from pathlib import Path


def kb_dir(book_dir: Path) -> Path:
    """Return the kb output directory inside a book folder, creating it if needed."""
    d = book_dir / "kb"
    d.mkdir(exist_ok=True)
    return d


def artifacts_dir(book_dir: Path) -> Path:
    """Return the kb/artifacts directory for intermediate files, creating it if needed."""
    d = book_dir / "kb" / "artifacts"
    d.mkdir(parents=True, exist_ok=True)
    return d


def source_md(book_dir: Path) -> Path:
    """Return path to the merged source file (<book_name>.md)."""
    return book_dir / f"{book_dir.name}.md"
