"""Command-line interface for minilog."""

import sys

from minilog import __version__


def main() -> None:
    """Entry point for the minilog CLI."""
    if len(sys.argv) >= 2 and sys.argv[1] == "version":
        print(f"minilog {__version__}")
    else:
        print(f"minilog {__version__}")
        print("Usage: minilog <command> [args]")
        print("Commands: version, run, repl, check")


if __name__ == "__main__":
    main()
