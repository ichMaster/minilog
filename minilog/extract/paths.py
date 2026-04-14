"""Path helpers for the extraction workflow."""

from pathlib import Path


def kb_dir(book_dir: Path) -> Path:
    """Return the kb output directory inside a book folder, creating it if needed."""
    d = book_dir / "kb"
    d.mkdir(exist_ok=True)
    return d
