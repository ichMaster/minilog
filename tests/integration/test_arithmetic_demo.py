"""Integration test for arithmetic_demo.ml example."""

import re
import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def _normalize_var_ids(text: str) -> str:
    """Replace object-id suffixes in renamed variables with a stable placeholder."""
    return re.sub(r"_(\d{7,})", "_ID", text)


def test_arithmetic_demo_output_matches_expected() -> None:
    """minilog run examples/arithmetic_demo.ml output matches expected."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "arithmetic_demo.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "arithmetic_demo.expected.txt").read_text(encoding="utf-8")
    assert _normalize_var_ids(result.stdout) == _normalize_var_ids(expected)
