"""Integration test for dwh_dependencies.ml example."""

import subprocess
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_dwh_dependencies_output_matches_expected() -> None:
    """minilog run examples/dwh_dependencies.ml output matches expected."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "dwh_dependencies.ml")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"minilog run failed: {result.stderr}"
    expected = (EXAMPLES_DIR / "dwh_dependencies.expected.txt").read_text(encoding="utf-8")
    assert result.stdout == expected


def test_dwh_detects_cycle() -> None:
    """dwh_dependencies.ml detects the seeded cycle."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "dwh_dependencies.ml")],
        capture_output=True, text=True,
    )
    assert "має_цикл" not in result.stderr  # no errors
    # The output should contain cycle detection results
    assert "sp_build_dim_customer" in result.stdout
    assert "sp_refresh_dim_customer" in result.stdout


def test_dwh_detects_write_conflict() -> None:
    """dwh_dependencies.ml detects write conflicts."""
    result = subprocess.run(
        [".venv/bin/minilog", "run", str(EXAMPLES_DIR / "dwh_dependencies.ml")],
        capture_output=True, text=True,
    )
    # Should find write conflicts on dim_customer and fact_sales
    assert "dim_customer" in result.stdout
    assert "fact_sales" in result.stdout
