"""Integration test for causality.ml example."""

import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_causality_output_matches_expected() -> None:
    """minilog run examples/causality.ml output matches causality.expected.txt."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "causality.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "causality.expected.txt").read_text(encoding="utf-8")
    assert result.stdout == expected
