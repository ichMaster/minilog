"""Step 4: Propose candidate rules — intra-domain and cross-domain."""

import json
from pathlib import Path

from minilog.extract.errors import DownloadError
from minilog.extract.llm import call_llm_json
from minilog.extract.paths import source_md
from minilog.extract.session import load_session, save_session


SYSTEM_PROMPT_INTRA = """You are an expert logic programmer. Given a set of extracted facts and a schema, propose useful minilog rules that capture patterns and relationships WITHIN each domain.

For each rule provide:
- "name": Ukrainian functor, lowercase
- "domain": which domain this rule belongs to
- "description": what the rule captures
- "head": rule head with variables
- "suggested_body_sketch": body goals separated by 'і'
- "is_recursive": true if the rule references itself
- "type": "intra-domain"

Include BOTH base cases and recursive rules. For example, if you have батько/2 facts, propose предок/2 with a base case AND a recursive case as two separate entries.

Output JSON array."""


SYSTEM_PROMPT_CROSS = """You are an expert knowledge engineer specializing in ontological analysis. Your task is to find CROSS-DOMAIN relationships, recursive patterns, and emergent knowledge that span multiple domains.

Given:
- Predicates and facts from multiple domains
- Existing intra-domain rules

Find:
1. **Cross-domain rules**: rules whose body uses predicates from 2+ different domains (e.g. "a bio-inspired algorithm uses a biological colony model")
2. **Cross-domain recursion**: transitive relationships that span domains (e.g. "X influences Y, Y influences Z → X indirectly influences Z" across domains)
3. **Emergent predicates**: NEW predicates not in the original schema that capture higher-level relationships discovered by combining domains (e.g. "міждисциплінарний_зв_язок/3" linking concepts across domains)
4. **Classification hierarchies**: rules that classify entities into categories based on multi-domain properties

For each rule provide:
- "name": Ukrainian functor, lowercase
- "domain": "cross-domain" or a new domain name
- "description": what the rule captures and which domains it connects
- "head": rule head with variables
- "suggested_body_sketch": body goals from multiple domains separated by 'і'
- "is_recursive": true if recursive
- "type": "cross-domain" | "emergent" | "recursive-cross"
- "connects_domains": list of domain names this rule bridges

Be creative but grounded — every predicate in the body must exist in the schema or be defined by another proposed rule.

Output JSON array."""


def propose_rules(book_dir: Path) -> list[dict]:
    """Propose rules in two substeps: intra-domain then cross-domain."""
    state = load_session(book_dir)
    schema = state.get("proposed_schema", {})
    facts = state.get("extracted_facts", [])

    if not schema:
        raise DownloadError(str(book_dir), "no schema — run propose-schema first")
    if not facts:
        raise DownloadError(str(book_dir), "no facts — run extract-facts first")

    schema_lines = _format_schema(schema)
    fact_summary = _format_facts_summary(facts)
    source_excerpt = _get_source_excerpt(book_dir)

    # Step 5a: Intra-domain rules
    print("  Step 5a: Proposing intra-domain rules...")
    intra_rules = _propose_intra(schema_lines, fact_summary, source_excerpt)
    print(f"    {len(intra_rules)} intra-domain rules proposed")

    # Step 5b: Cross-domain rules
    print("  Step 5b: Proposing cross-domain rules and emergent knowledge...")
    intra_summary = _format_rules_summary(intra_rules)
    cross_rules = _propose_cross(schema_lines, fact_summary, intra_summary)
    print(f"    {len(cross_rules)} cross-domain rules proposed")

    all_rules = intra_rules + cross_rules

    state["proposed_rules"] = all_rules
    state["current_step"] = "rules-proposed"
    save_session(book_dir, state)

    return all_rules


def _propose_intra(schema_lines: str, fact_summary: str, source_excerpt: str) -> list[dict]:
    """Step 5a: Propose intra-domain rules."""
    prompt = f"""Given the following schema and extracted facts, propose useful minilog rules WITHIN each domain.

## Schema (predicates by domain):
{schema_lines}

## Extracted facts summary:
{fact_summary}

## Source text excerpt:
{source_excerpt}

## Instructions:
1. Propose 5-15 rules per domain that capture meaningful patterns
2. Include BOTH base cases and recursive variants
3. For transitive relationships, always include base + recursive rule pair
4. Focus on rules useful for querying this knowledge base

Respond with JSON array only."""

    rules = call_llm_json(prompt, system=SYSTEM_PROMPT_INTRA, max_tokens=64000)
    if not isinstance(rules, list):
        return []
    for r in rules:
        r.setdefault("type", "intra-domain")
    return rules


def _propose_cross(schema_lines: str, fact_summary: str, intra_summary: str) -> list[dict]:
    """Step 5b: Propose cross-domain rules and emergent knowledge."""
    prompt = f"""Analyze these predicates, facts, and existing rules across ALL domains. Find cross-domain relationships, recursive patterns, and emergent knowledge.

## Schema (predicates by domain):
{schema_lines}

## Extracted facts summary:
{fact_summary}

## Existing intra-domain rules:
{intra_summary}

## Instructions:
1. Find rules whose body combines predicates from 2+ domains
2. Find transitive/recursive patterns that cross domain boundaries
3. Propose NEW emergent predicates that capture higher-level relationships
4. For each emergent predicate, provide both a defining rule and example usage
5. Propose at least 5 cross-domain rules
6. Every predicate in rule bodies must exist in the schema or be defined by another proposed rule

Respond with JSON array only."""

    rules = call_llm_json(prompt, system=SYSTEM_PROMPT_CROSS, max_tokens=64000)
    if not isinstance(rules, list):
        return []
    for r in rules:
        r.setdefault("type", "cross-domain")
    return rules


def _format_schema(schema: dict) -> str:
    lines = []
    for domain, preds in schema.items():
        lines.append(f"\n### {domain}")
        for p in preds:
            lines.append(f"  - {p['functor']}/{p['arity']}: {p.get('description', '')}")
    return "\n".join(lines)


def _format_facts_summary(facts: list[dict]) -> str:
    by_pred: dict[str, int] = {}
    for f in facts:
        if f.get("valid"):
            pred = f.get("predicate", "?")
            by_pred[pred] = by_pred.get(pred, 0) + 1
    return "\n".join(f"- {pred}: {count} facts" for pred, count in sorted(by_pred.items()))


def _format_rules_summary(rules: list[dict]) -> str:
    lines = []
    for r in rules:
        recursive = " (recursive)" if r.get("is_recursive") else ""
        lines.append(f"- {r.get('name', '?')}{recursive} [{r.get('domain', '?')}]: {r.get('description', '')}")
        if r.get("suggested_body_sketch"):
            lines.append(f"  sketch: {r['suggested_body_sketch']}")
    return "\n".join(lines)


def _get_source_excerpt(book_dir: Path) -> str:
    source_path = source_md(book_dir)
    if source_path.exists():
        return source_path.read_text(encoding="utf-8")[:10000]
    return ""
