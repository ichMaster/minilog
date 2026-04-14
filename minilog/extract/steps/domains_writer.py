"""Generate and update domains.md in the book folder."""

from pathlib import Path

from minilog.extract.session import load_session


def write_domains_md(book_dir: Path) -> Path:
    """Write domains.md from session state."""
    state = load_session(book_dir)
    detected = state.get("detected_domains", [])
    selected = state.get("selected_domains", [])
    schema = state.get("proposed_schema", {})
    grounding = state.get("grounding", {})

    lines = ["# Domains Report", ""]

    # Section 1: Detected domains
    lines.append("## Detected Domains")
    lines.append("")
    if detected:
        for d in detected:
            status = "SELECTED" if d["name"] in selected else "skipped"
            lines.append(f"- **{d['name']}** (relevance: {d.get('relevance', '?')}, {status})")
            lines.append(f"  {d.get('justification', '')}")
            if d.get("example_passage"):
                lines.append(f"  > \"{d['example_passage']}\"")
            lines.append("")
    else:
        lines.append("No domains detected yet.")
        lines.append("")

    # Section 2: Proposed schema
    if schema:
        lines.append("## Proposed Schema")
        lines.append("")
        for domain, preds in schema.items():
            lines.append(f"### {domain}")
            lines.append("")
            lines.append("| Predicate | Arity | Status | Description |")
            lines.append("|-----------|-------|--------|-------------|")
            for p in preds:
                key = f"{p['functor']}/{p['arity']}"
                is_grounded = grounding.get(key, {}).get("grounded", False)
                status = "grounded" if is_grounded else "theoretical"
                lines.append(f"| `{p['functor']}` | {p['arity']} | {status} | {p.get('description', '')} |")
            lines.append("")

    # Section 3: Grounding statistics
    if grounding:
        lines.append("## Grounding Statistics")
        lines.append("")
        total = len(grounding)
        grounded = sum(1 for v in grounding.values() if v.get("grounded"))
        lines.append(f"- Total predicates: {total}")
        lines.append(f"- Grounded: {grounded}")
        lines.append(f"- Theoretical: {total - grounded}")
        lines.append("")

    from minilog.extract.paths import kb_dir
    domains_path = kb_dir(book_dir) / "domains.md"
    domains_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return domains_path
