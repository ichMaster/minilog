"""Converters for various source formats."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConversionResult:
    """Result of converting a source to Markdown."""
    original_path: Path
    markdown_path: Path
    title: str | None = None
    author: str | None = None
    language: str | None = None
    source_url: str | None = None
