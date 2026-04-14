"""Step 5: Generate concrete rule bodies and validate them."""

import json
from pathlib import Path

from minilog.extract.errors import DownloadError
from minilog.extract.llm import call_llm_json
from minilog.extract.session import load_session, save_session


SYSTEM_PROMPT = """You are an expert minilog programmer. Generate concrete rule bodies in minilog syntax for proposed rules.

minilog syntax:
- правило head якщо body.
- Body goals separated by 'і'
- Variables start with ?
- Negation: не predicate(...)
- Comparison: ?x > ?y, ?x = ?y, ?x != ?y

Output JSON array:
[
  {
    "name": "предок",
    "rule_text": "правило предок(?x, ?y) якщо батько(?x, ?y).",
    "variant": "base"
  },
  {
    "name": "предок",
    "rule_text": "правило предок(?x, ?z) якщо батько(?x, ?y) і предок(?y, ?z).",
    "variant": "recursive"
  }
]"""


def generate_rules(book_dir: Path, selected_rules: list[str] | None = None) -> list[dict]:
    """Generate concrete minilog rules for selected candidates."""
    state = load_session(book_dir)
    proposed = state.get("proposed_rules", [])

    if not proposed:
        raise DownloadError(str(book_dir), "no proposed rules — run propose-rules first")

    if selected_rules:
        proposed = [r for r in proposed if r.get("name") in selected_rules]

    schema = state.get("proposed_schema", {})
    schema_lines = []
    for domain, preds in schema.items():
        for p in preds:
            schema_lines.append(f"- {p['functor']}/{p['arity']}: {p.get('description', '')}")

    rule_descriptions = []
    for r in proposed:
        rule_descriptions.append(
            f"- {r['name']}: {r.get('description', '')} "
            f"(head: {r.get('head', '?')}, sketch: {r.get('suggested_body_sketch', '?')})"
        )

    prompt = f"""Generate concrete minilog rules for the following candidates.

## Available predicates (schema):
{chr(10).join(schema_lines)}

## Rules to generate:
{chr(10).join(rule_descriptions)}

## Instructions:
1. For each rule candidate, produce one or more concrete minilog rules
2. Use 'правило' keyword, 'якщо' for body, 'і' for conjunction
3. Variables start with ?
4. Include base cases and recursive variants where appropriate
5. Each rule must end with a dot (.)

Respond with JSON array only."""

    generated = call_llm_json(prompt, system=SYSTEM_PROMPT, max_tokens=64000)

    if not isinstance(generated, list):
        raise DownloadError(str(book_dir), f"LLM returned non-list: {type(generated)}")

    # Validate syntax
    validated = _validate_rules(generated, schema)

    state["generated_rules"] = validated
    state["current_step"] = "rules-generated"
    save_session(book_dir, state)

    # Write rules.ml
    _write_rules_ml(book_dir, validated)

    return validated


def _validate_rules(rules: list[dict], schema: dict) -> list[dict]:
    """Validate rule syntax and predicate references."""
    valid_preds: set[str] = set()
    for domain, preds in schema.items():
        for p in preds:
            valid_preds.add(p["functor"])

    # Also add comparison built-ins
    valid_preds.update({"не", "і"})

    for rule in rules:
        rule_text = rule.get("rule_text", "")
        issues = []

        # Basic syntax check
        if not rule_text.strip().startswith("правило"):
            issues.append("rule must start with 'правило'")
        if not rule_text.strip().endswith("."):
            issues.append("rule must end with '.'")
        if "якщо" not in rule_text:
            issues.append("rule must contain 'якщо'")

        # Try parsing with minilog parser
        try:
            from minilog.parser import parse
            parse(rule_text)
            rule["syntax_valid"] = True
        except Exception as e:
            issues.append(f"parse error: {e}")
            rule["syntax_valid"] = False

        rule["issues"] = issues
        rule["valid"] = len(issues) == 0 or rule.get("syntax_valid", False)

    return rules


def _write_rules_ml(book_dir: Path, rules: list[dict]) -> None:
    """Write rules.ml with generated rules."""
    lines = ["% Rules generated from proposed candidates", ""]

    for r in rules:
        if not r.get("valid", True):
            lines.append(f"% INVALID: {r.get('name', '?')} — {', '.join(r.get('issues', []))}")
            lines.append(f"% {r.get('rule_text', '')}")
        else:
            lines.append(f"% {r.get('name', '?')}: {r.get('variant', '')}")
            lines.append(r.get("rule_text", ""))
        lines.append("")

    rules_path = book_dir / "rules.ml"
    rules_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
