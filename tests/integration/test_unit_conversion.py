"""Integration test for unit_conversion.ml example."""

import re
import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def _normalize_var_ids(text: str) -> str:
    return re.sub(r"_(\d{2,})", "_ID", text)


def test_unit_conversion_output_matches_expected() -> None:
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "unit_conversion.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "unit_conversion.expected.txt").read_text(encoding="utf-8")
    assert _normalize_var_ids(result.stdout) == _normalize_var_ids(expected)
