"""Integration test for family.ml example."""

import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_family_output_matches_expected() -> None:
    """minilog run examples/family.ml output matches family.expected.txt."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "family.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "family.expected.txt").read_text(encoding="utf-8")
    assert result.stdout == expected
