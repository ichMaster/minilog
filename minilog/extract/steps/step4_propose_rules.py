"""Step 4: Propose candidate rules from domains and facts."""

import json
from pathlib import Path

from minilog.extract.errors import DownloadError
from minilog.extract.llm import call_llm_json
from minilog.extract.session import load_session, save_session


SYSTEM_PROMPT = """You are an expert logic programmer. Given a set of extracted facts and a schema, propose useful minilog rules that capture patterns and relationships in the data.

Each rule should have:
- A name (Ukrainian functor, lowercase)
- A natural-language description of what the rule captures
- The domain it belongs to
- Why it would be useful

Output JSON array:
[
  {
    "name": "предок",
    "domain": "family",
    "description": "Transitive ancestry: X is ancestor of Y if X is parent of Z and Z is ancestor of Y",
    "head": "предок(?x, ?y)",
    "suggested_body_sketch": "батько(?x, ?z) і предок(?z, ?y)"
  }
]"""


def propose_rules(book_dir: Path) -> list[dict]:
    """Propose candidate rules based on extracted facts and schema."""
    state = load_session(book_dir)
    schema = state.get("proposed_schema", {})
    facts = state.get("extracted_facts", [])

    if not schema:
        raise DownloadError(str(book_dir), "no schema — run propose-schema first")
    if not facts:
        raise DownloadError(str(book_dir), "no facts — run extract-facts first")

    # Summarize facts for the prompt
    fact_summary = []
    by_pred: dict[str, int] = {}
    for f in facts:
        if f.get("valid"):
            pred = f.get("predicate", "?")
            by_pred[pred] = by_pred.get(pred, 0) + 1
    for pred, count in sorted(by_pred.items()):
        fact_summary.append(f"- {pred}: {count} facts")

    # Summarize schema
    schema_lines = []
    for domain, preds in schema.items():
        for p in preds:
            schema_lines.append(f"- {p['functor']}/{p['arity']} ({domain}): {p.get('description', '')}")

    source_path = book_dir / "source.md"
    source_excerpt = ""
    if source_path.exists():
        source_excerpt = source_path.read_text(encoding="utf-8")[:10000]

    prompt = f"""Given the following schema and extracted facts, propose useful minilog rules.

## Schema:
{chr(10).join(schema_lines)}

## Extracted facts summary:
{chr(10).join(fact_summary)}

## Source text excerpt (for context):
{source_excerpt}

## Instructions:
1. Propose 5-15 rules that capture meaningful patterns
2. Rules should use predicates from the schema
3. Include both base cases and recursive rules where appropriate
4. Focus on rules that would be actually useful for querying this knowledge base

Respond with JSON array only."""

    rules = call_llm_json(prompt, system=SYSTEM_PROMPT, max_tokens=64000)

    if not isinstance(rules, list):
        raise DownloadError(str(book_dir), f"LLM returned non-list: {type(rules)}")

    state["proposed_rules"] = rules
    state["current_step"] = "rules-proposed"
    save_session(book_dir, state)

    return rules
