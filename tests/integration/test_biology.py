"""Integration test for biology.ml example."""

import re
import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def _normalize_var_ids(text: str) -> str:
    """Replace object-id suffixes in renamed variables with a stable placeholder."""
    return re.sub(r"_(\d{7,})", "_ID", text)


def test_biology_output_matches_expected() -> None:
    """minilog run examples/biology.ml output matches biology.expected.txt."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "biology.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "biology.expected.txt").read_text(encoding="utf-8")
    # Normalize object IDs in traced output for stable comparison
    assert _normalize_var_ids(result.stdout) == _normalize_var_ids(expected)


def test_biology_flies_query() -> None:
    """biology.ml correctly answers літає(?x)."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "biology.ml")],
        capture_output=True, text=True,
    )
    assert "горобець" in result.stdout
    assert "орел" in result.stdout
    # Penguin should NOT fly
    assert "пінгвін" not in result.stdout.split("(2 solutions)")[0]


def test_biology_trace_has_box_drawing() -> None:
    """The traced query produces output with box-drawing characters."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "biology.ml")],
        capture_output=True, text=True,
    )
    assert "├─" in result.stdout or "└─" in result.stdout
