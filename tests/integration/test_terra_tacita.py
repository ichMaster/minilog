"""Integration test for terra_tacita.ml example."""

import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_terra_tacita_output_matches_expected() -> None:
    """minilog run examples/terra_tacita.ml output matches terra_tacita.expected.txt."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "terra_tacita.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "terra_tacita.expected.txt").read_text(encoding="utf-8")
    assert result.stdout == expected


def test_terra_tacita_has_disclaimer() -> None:
    """terra_tacita.ml starts with the required disclaimer comment."""
    source = (EXAMPLES_DIR / "terra_tacita.ml").read_text(encoding="utf-8")
    assert source.startswith("% =")
    assert "НАВЧАЛЬНИЙ ПРИКЛАД" in source or "TEACHING EXAMPLE" in source
    assert "NOT" in source or "НЕ" in source
