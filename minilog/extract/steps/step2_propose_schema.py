"""Step 2: Propose schema predicates per domain and ground them against text."""

import json
from pathlib import Path

from minilog.extract.errors import DownloadError
from minilog.extract.llm import call_llm_json
from minilog.extract.session import load_session, save_session


PROPOSE_SYSTEM = """You are an expert knowledge engineer specializing in logic programming. Your task is to propose minilog predicates for specific knowledge domains found in a text.

For each domain, propose 3-8 predicates that capture the key relationships in the text. Each predicate should have:
- A Ukrainian functor name (following minilog conventions)
- An arity (number of arguments)
- Argument role descriptions

Respond with a JSON object where keys are domain names and values are arrays of predicate objects:
{
  "domain_name": [
    {"functor": "батько", "arity": 2, "args": ["батько: atom", "дитина: atom"], "description": "parent-child relationship"}
  ]
}"""


GROUNDING_SYSTEM = """You are a fact-checking assistant. For each proposed predicate, find 2-3 concrete examples in the source text where that predicate could be applied. Quote short passages (max 80 chars) as evidence.

Respond with a JSON object where keys are "functor/arity" strings and values are objects:
{
  "батько/2": {
    "grounded": true,
    "examples": [
      {"args": ["авраам", "ісак"], "citation": "Авраам народив Ісака..."}
    ]
  }
}

If no examples can be found in the text, set "grounded" to false and "examples" to an empty array."""


def propose_predicates(book_dir: Path, selected_domains: list[str] | None = None) -> dict:
    """Step 2a: Propose predicates for selected domains."""
    source_path = book_dir / "source.md"
    if not source_path.exists():
        raise DownloadError(str(book_dir), "source.md not found")

    state = load_session(book_dir)
    detected = state.get("detected_domains", [])
    if not detected:
        raise DownloadError(str(book_dir), "no detected domains — run detect-domains first")

    # Use all detected domains if none selected
    if selected_domains is None:
        selected_domains = [d["name"] for d in detected]

    source_text = source_path.read_text(encoding="utf-8")
    if len(source_text) > 50000:
        source_text = source_text[:50000] + "\n\n[... truncated ...]"

    domain_descriptions = []
    for d in detected:
        if d["name"] in selected_domains:
            domain_descriptions.append(f"- {d['name']}: {d.get('justification', '')}")

    prompt = f"""Propose minilog predicates for these knowledge domains found in the text:

{chr(10).join(domain_descriptions)}

## Source text (for context):
{source_text[:20000]}

## Instructions:
For each domain, propose 3-8 predicates with Ukrainian functor names, arities, argument roles, and short descriptions. Only propose predicates that are actually applicable to THIS text.

Respond with JSON only."""

    schema = call_llm_json(prompt, system=PROPOSE_SYSTEM, max_tokens=4096)

    state["proposed_schema"] = schema
    state["selected_domains"] = selected_domains
    save_session(book_dir, state)

    return schema


def grounding_check(book_dir: Path) -> dict:
    """Step 2b: Check each proposed predicate against the source text."""
    source_path = book_dir / "source.md"
    state = load_session(book_dir)
    schema = state.get("proposed_schema")
    if not schema:
        raise DownloadError(str(book_dir), "no proposed schema — run propose-schema first")

    source_text = source_path.read_text(encoding="utf-8")
    if len(source_text) > 50000:
        source_text = source_text[:50000] + "\n\n[... truncated ...]"

    # Flatten predicates for the prompt
    all_preds = []
    for domain, preds in schema.items():
        for p in preds:
            all_preds.append(f"- {p['functor']}/{p['arity']}: {p.get('description', '')}")

    prompt = f"""For each predicate below, find 2-3 concrete examples in the source text where it applies. Quote short passages as evidence.

## Predicates to ground:
{chr(10).join(all_preds)}

## Source text:
{source_text[:30000]}

Respond with JSON only. Use "functor/arity" as keys."""

    grounding = call_llm_json(prompt, system=GROUNDING_SYSTEM, max_tokens=4096)

    state["grounding"] = grounding
    state["current_step"] = "schema-done"
    save_session(book_dir, state)

    # Write schema.ml
    _write_schema_ml(book_dir, schema, grounding)

    # Write grounding results
    grounding_path = book_dir / "grounding.json"
    grounding_path.write_text(json.dumps(grounding, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return grounding


def _write_schema_ml(book_dir: Path, schema: dict, grounding: dict) -> None:
    """Write schema.ml with predicate declarations as comments."""
    lines = ["% Schema — proposed predicates for knowledge extraction", ""]

    for domain, preds in schema.items():
        lines.append(f"% Domain: {domain}")
        for p in preds:
            key = f"{p['functor']}/{p['arity']}"
            is_grounded = grounding.get(key, {}).get("grounded", False)
            status = "grounded" if is_grounded else "theoretical"
            args_desc = ", ".join(p.get("args", []))
            lines.append(f"% {key} ({status}) — {p.get('description', '')} — args: {args_desc}")
        lines.append("")

    schema_path = book_dir / "schema.ml"
    schema_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
