"""Session state management for extraction workflow."""

import json
from pathlib import Path


SESSION_FILE = ".session.json"


def load_session(book_dir: Path) -> dict:
    """Load session state from book folder. Returns empty dict if no session."""
    session_path = book_dir / SESSION_FILE
    if session_path.exists():
        return json.loads(session_path.read_text(encoding="utf-8"))
    return {}


def save_session(book_dir: Path, state: dict) -> None:
    """Save session state to book folder."""
    session_path = book_dir / SESSION_FILE
    session_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_step(book_dir: Path) -> str:
    """Get the current workflow step."""
    state = load_session(book_dir)
    return state.get("current_step", "download")


def set_step(book_dir: Path, step: str) -> None:
    """Set the current workflow step."""
    state = load_session(book_dir)
    state["current_step"] = step
    save_session(book_dir, state)
