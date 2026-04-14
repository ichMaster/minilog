"""Step 3: Extract facts from source text using approved schema."""

import json
from pathlib import Path

from minilog.extract.errors import DownloadError
from minilog.extract.llm import call_llm_json
from minilog.extract.session import load_session, save_session


SYSTEM_PROMPT = """You are an expert knowledge engineer. Your task is to extract concrete ground facts from a text that match a given schema of minilog predicates. Each fact must have a citation — a short quoted passage from the source text that supports it.

Output format: JSON array of objects:
[
  {
    "predicate": "батько",
    "arity": 2,
    "args": ["авраам", "ісак"],
    "citation": "Abraham begat Isaac..."
  }
]

Rules:
1. Only use predicates from the provided schema.
2. Arguments must be atoms (lowercase identifiers) — no spaces, no special characters.
3. Each citation must be a short passage (max 100 chars) actually found in the source text.
4. Do not invent facts not supported by the text.
5. Be thorough — extract ALL facts the text supports for each predicate."""


def _chunk_text(text: str, max_chars: int = 40000, overlap: int = 2000) -> list[str]:
    """Split text into overlapping chunks."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def _format_schema_for_prompt(book_dir: Path) -> str:
    """Read schema from session and format for the prompt."""
    state = load_session(book_dir)
    schema = state.get("proposed_schema", {})
    lines = []
    for domain, preds in schema.items():
        for p in preds:
            args = ", ".join(p.get("args", [f"arg{i+1}" for i in range(p["arity"])]))
            lines.append(f"- {p['functor']}/{p['arity']} ({args}) — {p.get('description', '')}")
    return "\n".join(lines)


def extract_facts(book_dir: Path) -> list[dict]:
    """Extract facts from source text using the approved schema."""
    source_path = book_dir / "source.md"
    if not source_path.exists():
        raise DownloadError(str(book_dir), "source.md not found")

    state = load_session(book_dir)
    if not state.get("proposed_schema"):
        raise DownloadError(str(book_dir), "no schema — run propose-schema first")

    schema_text = _format_schema_for_prompt(book_dir)
    source_text = source_path.read_text(encoding="utf-8")
    chunks = _chunk_text(source_text)

    all_facts: list[dict] = []
    seen_keys: set[str] = set()

    for i, chunk in enumerate(chunks):
        prompt = f"""Extract all ground facts from the following text chunk that match the schema below.

## Schema (predicates to use):
{schema_text}

## Text (chunk {i+1}/{len(chunks)}):
{chunk}

Respond with a JSON array only."""

        try:
            facts = call_llm_json(prompt, system=SYSTEM_PROMPT, max_tokens=8192)
        except DownloadError:
            continue  # Skip failed chunks

        if not isinstance(facts, list):
            continue

        # Deduplicate across chunks
        for fact in facts:
            key = f"{fact.get('predicate')}/{fact.get('arity')}({','.join(fact.get('args', []))})"
            if key not in seen_keys:
                seen_keys.add(key)
                all_facts.append(fact)

    # Validate facts
    validated = _validate_facts(all_facts, book_dir, source_text)

    # Save to session
    state["extracted_facts"] = validated
    state["current_step"] = "facts-done"
    save_session(book_dir, state)

    # Write facts.ml
    _write_facts_ml(book_dir, validated)

    return validated


def _validate_facts(facts: list[dict], book_dir: Path, source_text: str) -> list[dict]:
    """Validate facts against schema and source text."""
    state = load_session(book_dir)
    schema = state.get("proposed_schema", {})

    # Build set of valid predicates
    valid_preds: set[str] = set()
    for domain, preds in schema.items():
        for p in preds:
            valid_preds.add(f"{p['functor']}/{p['arity']}")

    validated = []
    source_lower = source_text.lower()

    for fact in facts:
        key = f"{fact.get('predicate')}/{fact.get('arity')}"
        issues = []

        # Check predicate exists in schema
        if key not in valid_preds:
            issues.append(f"unknown predicate {key}")

        # Check arity matches args count
        args = fact.get("args", [])
        if len(args) != fact.get("arity", 0):
            issues.append(f"arity mismatch: declared {fact.get('arity')}, got {len(args)} args")

        # Check citation exists in source (case-insensitive, whitespace-normalized)
        citation = fact.get("citation", "")
        if citation:
            citation_normalized = " ".join(citation.lower().split())
            if citation_normalized not in " ".join(source_lower.split()):
                issues.append("citation not found in source")

        fact["valid"] = len(issues) == 0
        fact["issues"] = issues
        validated.append(fact)

    return validated


def _write_facts_ml(book_dir: Path, facts: list[dict]) -> None:
    """Write facts.ml with citations as comments."""
    lines = ["% Facts extracted from source text", "% Each fact followed by citation comment", ""]

    # Group by predicate
    by_pred: dict[str, list[dict]] = {}
    for f in facts:
        if not f.get("valid", True):
            continue
        pred = f.get("predicate", "unknown")
        by_pred.setdefault(pred, []).append(f)

    for pred, pred_facts in sorted(by_pred.items()):
        lines.append(f"% {pred}")
        for f in pred_facts:
            args = ", ".join(f.get("args", []))
            citation = f.get("citation", "")
            lines.append(f"{pred}({args}).  % \"{citation}\"")
        lines.append("")

    facts_path = book_dir / "facts.ml"
    facts_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
