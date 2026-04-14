"""Step 1: Detect knowledge domains in source text."""

import json
from pathlib import Path

from minilog.extract.domains import format_catalog_for_prompt
from minilog.extract.errors import DownloadError
from minilog.extract.paths import source_md
from minilog.extract.llm import call_llm_json
from minilog.extract.session import load_session, save_session


SYSTEM_PROMPT = """You are an expert knowledge engineer. Your task is to identify which knowledge domains are present in a given text. You will be provided with a catalog of known domains and must identify which ones are relevant, plus any novel domains not in the catalog.

Respond with a JSON array of objects, each with:
- "name": domain name (lowercase, underscore-separated)
- "relevance": float 0.0-1.0 (how relevant this domain is to the text)
- "justification": one sentence explaining why this domain is present
- "example_passage": a short quote from the text (max 100 chars) that illustrates this domain
- "is_catalog": boolean (true if from the built-in catalog, false if novel)

Only include domains with relevance >= 0.5. Sort by relevance descending."""


def detect_domains(book_dir: Path) -> list[dict]:
    """Run domain detection on the source text."""
    source_path = source_md(book_dir)
    if not source_path.exists():
        raise DownloadError(str(book_dir), f"{source_path.name} not found — run download first")

    source_text = source_path.read_text(encoding="utf-8")
    # Truncate to ~50K chars for LLM context
    if len(source_text) > 50000:
        source_text = source_text[:50000] + "\n\n[... truncated ...]"

    catalog = format_catalog_for_prompt()

    prompt = f"""Analyze the following text and identify which knowledge domains are present.

## Built-in domain catalog:
{catalog}

## Text to analyze:
{source_text}

## Instructions:
1. Check each domain from the catalog — is it present in the text?
2. If you see domains NOT in the catalog, add them as novel domains.
3. Only include domains with relevance >= 0.5.
4. For each domain, provide a justification and a short example passage from the text.

Respond with a JSON array only, no additional text."""

    domains = call_llm_json(prompt, system=SYSTEM_PROMPT, max_tokens=64000)

    if not isinstance(domains, list):
        raise DownloadError(str(book_dir), f"LLM returned non-list response: {type(domains)}")

    # Save to session
    state = load_session(book_dir)
    state["detected_domains"] = domains
    state["current_step"] = "detect-domains-done"
    save_session(book_dir, state)

    # Write domains to a JSON file for easy inspection
    from minilog.extract.paths import artifacts_dir
    out = artifacts_dir(book_dir)
    domains_json = out / "detected_domains.json"
    domains_json.write_text(json.dumps(domains, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return domains
