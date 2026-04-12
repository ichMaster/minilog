"""Integration test for directions.ml example."""

import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_directions_output_matches_expected() -> None:
    """minilog run examples/directions.ml output matches directions.expected.txt."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "directions.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "directions.expected.txt").read_text(encoding="utf-8")
    assert result.stdout == expected
