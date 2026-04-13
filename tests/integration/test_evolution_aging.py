"""Integration test for evolution_aging.ml example."""

import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_evolution_aging_baseline() -> None:
    """minilog run examples/evolution_aging.ml baseline output matches expected."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "evolution_aging.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "evolution_aging.expected.txt").read_text(encoding="utf-8")
    assert result.stdout == expected
