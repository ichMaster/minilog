"""Integration test for mythology.ml example."""

import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_mythology_output_matches_expected() -> None:
    """minilog run examples/mythology.ml output matches mythology.expected.txt."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "mythology.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "mythology.expected.txt").read_text(encoding="utf-8")
    assert result.stdout == expected
