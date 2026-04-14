"""CLI for minilog text extraction: download, detect-domains, etc."""

import os
import shutil
import sys
from pathlib import Path

from minilog.extract.errors import DownloadError


def _get_kb_dir() -> Path:
    """Get the knowledge bases directory."""
    env = os.environ.get("MINILOG_KB_DIR")
    if env:
        return Path(env)
    return Path.cwd() / "knowledge_bases"


def _classify_source(source: str) -> str:
    """Classify source as 'url' or a file extension."""
    if source.startswith("http://") or source.startswith("https://"):
        return "url"
    path = Path(source)
    ext = path.suffix.lower()
    if ext in (".pdf", ".docx", ".epub", ".txt", ".md", ".html", ".htm"):
        return ext
    return ext or "unknown"


def _convert_source(source: str, source_type: str, target_dir: Path):
    """Dispatch to the appropriate converter."""
    from minilog.extract.converters import ConversionResult

    if source_type == "url":
        from minilog.extract.converters.html_url import download_html
        return download_html(source, target_dir)
    elif source_type == ".pdf":
        from minilog.extract.converters.pdf_file import convert_pdf
        return convert_pdf(Path(source), target_dir)
    elif source_type == ".docx":
        from minilog.extract.converters.docx_file import convert_docx
        return convert_docx(Path(source), target_dir)
    elif source_type == ".epub":
        from minilog.extract.converters.epub_file import convert_epub
        return convert_epub(Path(source), target_dir)
    elif source_type == ".txt":
        from minilog.extract.converters.text_file import convert_txt
        return convert_txt(Path(source), target_dir)
    elif source_type in (".md",):
        from minilog.extract.converters.text_file import convert_md
        return convert_md(Path(source), target_dir)
    elif source_type in (".html", ".htm"):
        from minilog.extract.converters.html_file import convert_html_file
        return convert_html_file(Path(source), target_dir)
    else:
        raise DownloadError(source, f"unsupported file format: {source_type}")


def cmd_download(args) -> None:
    """Execute the download command."""
    from minilog.extract.merge import merge_sources
    from minilog.extract.metadata import write_metadata

    name = args.name
    sources_raw = args.sources
    sources = [s.strip() for s in sources_raw.split(",") if s.strip()]

    if not sources:
        print("Error: --sources must contain at least one source", file=sys.stderr)
        sys.exit(1)

    kb_dir = _get_kb_dir()
    target_dir = kb_dir / name

    if target_dir.exists():
        print(f"Error: book folder already exists: {target_dir}", file=sys.stderr)
        sys.exit(1)

    # Create the folder
    target_dir.mkdir(parents=True)

    results = []
    try:
        for source in sources:
            source_type = _classify_source(source)
            print(f"  Converting {source} ({source_type})...")
            result = _convert_source(source, source_type, target_dir)
            results.append(result)

        # Merge and write metadata
        merge_sources(results, target_dir)
        write_metadata(
            target_dir, name, results,
            title_override=args.title,
            author_override=args.author,
            language_override=args.language,
        )

        print(f"Done. Book folder created: {target_dir}")
        print(f"  {len(results)} source(s) converted")
        print(f"  source.md and metadata.txt written")

    except (DownloadError, Exception) as e:
        # Rollback: remove the partially populated folder
        print(f"Error: {e}", file=sys.stderr)
        if target_dir.exists():
            shutil.rmtree(target_dir)
            print(f"Rolled back: removed {target_dir}", file=sys.stderr)
        sys.exit(1)


def register_extract_subcommand(subparsers) -> None:
    """Register the 'extract' subcommand family."""
    import argparse

    extract_parser = subparsers.add_parser("extract", help="Text extraction commands")
    extract_sub = extract_parser.add_subparsers(dest="extract_command")

    # download
    dl = extract_sub.add_parser("download", help="Download and convert sources into a book folder")
    dl.add_argument("--name", required=True, help="Book folder name")
    dl.add_argument("--sources", required=True, help="Comma-separated list of URLs or file paths")
    dl.add_argument("--title", default=None, help="Override auto-detected title")
    dl.add_argument("--author", default=None, help="Override auto-detected author")
    dl.add_argument("--language", default=None, help="Override auto-detected language")
    dl.set_defaults(func=_handle_extract)

    # detect-domains
    dd = extract_sub.add_parser("detect-domains", help="Detect knowledge domains in source text (LLM)")
    dd.add_argument("--name", required=True, help="Book folder name")
    dd.set_defaults(func=_handle_extract)

    # propose-schema
    ps = extract_sub.add_parser("propose-schema", help="Propose predicates and ground them (LLM)")
    ps.add_argument("--name", required=True, help="Book folder name")
    ps.add_argument("--domains", default=None, help="Comma-separated domain names to include (default: all detected)")
    ps.set_defaults(func=_handle_extract)

    # extract-facts
    ef = extract_sub.add_parser("extract-facts", help="Extract facts from source text (LLM)")
    ef.add_argument("--name", required=True, help="Book folder name")
    ef.set_defaults(func=_handle_extract)

    # propose-rules
    pr = extract_sub.add_parser("propose-rules", help="Propose candidate rules (LLM)")
    pr.add_argument("--name", required=True, help="Book folder name")
    pr.set_defaults(func=_handle_extract)

    # generate-rules
    gr = extract_sub.add_parser("generate-rules", help="Generate rule bodies (LLM)")
    gr.add_argument("--name", required=True, help="Book folder name")
    gr.add_argument("--rules", default=None, help="Comma-separated rule names (default: all proposed)")
    gr.set_defaults(func=_handle_extract)

    # finalize
    fn = extract_sub.add_parser("finalize", help="Merge into knowledge_base.ml")
    fn.add_argument("--name", required=True, help="Book folder name")
    fn.set_defaults(func=_handle_extract)

    # run-all (steps 2-8: detect-domains → propose-schema → extract-facts → propose-rules → generate-rules → finalize)
    ra = extract_sub.add_parser("run-all", help="Run all extraction steps (2-8) after download")
    ra.add_argument("--name", required=True, help="Book folder name")
    ra.set_defaults(func=_handle_extract)


def cmd_detect_domains(args) -> None:
    """Execute detect-domains command."""
    from minilog.extract.steps.step1_detect_domains import detect_domains
    from minilog.extract.steps.domains_writer import write_domains_md

    book_dir = _get_kb_dir() / args.name
    if not book_dir.exists():
        print(f"Error: book folder not found: {book_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Detecting domains in {book_dir}/source.md...")
    try:
        domains = detect_domains(book_dir)
        write_domains_md(book_dir)
    except DownloadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Detected {len(domains)} domain(s):")
    for d in domains:
        print(f"  {d['name']} (relevance: {d.get('relevance', '?')}): {d.get('justification', '')}")
    print(f"\nResults saved to {book_dir}/detected_domains.json and {book_dir}/domains.md")


def cmd_propose_schema(args) -> None:
    """Execute propose-schema command (Step 2a + 2b)."""
    from minilog.extract.steps.step2_propose_schema import propose_predicates, grounding_check
    from minilog.extract.steps.domains_writer import write_domains_md

    book_dir = _get_kb_dir() / args.name
    if not book_dir.exists():
        print(f"Error: book folder not found: {book_dir}", file=sys.stderr)
        sys.exit(1)

    selected = None
    if args.domains:
        selected = [d.strip() for d in args.domains.split(",")]

    print(f"Step 2a: Proposing predicates...")
    try:
        schema = propose_predicates(book_dir, selected_domains=selected)
    except DownloadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    total_preds = sum(len(preds) for preds in schema.values())
    print(f"  Proposed {total_preds} predicates across {len(schema)} domain(s)")

    print(f"Step 2b: Grounding check...")
    try:
        grounding = grounding_check(book_dir)
        write_domains_md(book_dir)
    except DownloadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    grounded = sum(1 for v in grounding.values() if v.get("grounded"))
    print(f"  {grounded}/{len(grounding)} predicates grounded in text")
    print(f"\nResults saved to {book_dir}/schema.ml, {book_dir}/grounding.json, {book_dir}/domains.md")


def cmd_extract_facts(args) -> None:
    """Execute extract-facts command."""
    from minilog.extract.steps.step3_extract_facts import extract_facts

    book_dir = _get_kb_dir() / args.name
    if not book_dir.exists():
        print(f"Error: book folder not found: {book_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting facts from {book_dir}/source.md...")
    try:
        facts = extract_facts(book_dir)
    except DownloadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    valid = sum(1 for f in facts if f.get("valid"))
    invalid = len(facts) - valid
    print(f"Extracted {len(facts)} facts ({valid} valid, {invalid} with issues)")
    print(f"Results saved to {book_dir}/facts.ml")


def cmd_propose_rules(args) -> None:
    """Execute propose-rules command."""
    from minilog.extract.steps.step4_propose_rules import propose_rules

    book_dir = _get_kb_dir() / args.name
    if not book_dir.exists():
        print(f"Error: book folder not found: {book_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Proposing rules...")
    try:
        rules = propose_rules(book_dir)
    except DownloadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Proposed {len(rules)} rule candidate(s):")
    for r in rules:
        print(f"  {r.get('name', '?')}: {r.get('description', '')}")
    print(f"\nResults saved to session.")


def cmd_generate_rules(args) -> None:
    """Execute generate-rules command."""
    from minilog.extract.steps.step5_generate_rules import generate_rules

    book_dir = _get_kb_dir() / args.name
    if not book_dir.exists():
        print(f"Error: book folder not found: {book_dir}", file=sys.stderr)
        sys.exit(1)

    selected = None
    if hasattr(args, "rules") and args.rules:
        selected = [r.strip() for r in args.rules.split(",")]

    print(f"Generating rule bodies...")
    try:
        rules = generate_rules(book_dir, selected_rules=selected)
    except DownloadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    valid = sum(1 for r in rules if r.get("valid"))
    print(f"Generated {len(rules)} rules ({valid} valid)")
    print(f"Results saved to {book_dir}/rules.ml")


def cmd_finalize(args) -> None:
    """Execute finalize command."""
    from minilog.extract.steps.finalize import finalize

    book_dir = _get_kb_dir() / args.name
    if not book_dir.exists():
        print(f"Error: book folder not found: {book_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Finalizing knowledge base...")
    try:
        kb_path = finalize(book_dir)
    except DownloadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Knowledge base written to {kb_path}")
    print(f"Load it with: minilog repl {kb_path}")


def cmd_run_all(args) -> None:
    """Execute all extraction steps (2-8) after download."""
    book_dir = _get_kb_dir() / args.name
    if not book_dir.exists():
        print(f"Error: book folder not found: {book_dir}", file=sys.stderr)
        print(f"Run 'minilog extract download --name {args.name} --sources ...' first.")
        sys.exit(1)

    if not (book_dir / "source.md").exists():
        print(f"Error: source.md not found in {book_dir}", file=sys.stderr)
        sys.exit(1)

    steps = [
        ("Step 2: Detecting domains...", cmd_detect_domains),
        ("Step 3: Proposing schema...", cmd_propose_schema),
        ("Step 4: Extracting facts...", cmd_extract_facts),
        ("Step 5: Proposing rules...", cmd_propose_rules),
        ("Step 6: Generating rules...", cmd_generate_rules),
        ("Step 7: Finalizing...", cmd_finalize),
    ]

    print(f"Running full extraction pipeline on '{args.name}'...")
    print(f"{'=' * 50}")

    for label, cmd_func in steps:
        print(f"\n{label}")
        print(f"{'-' * 50}")
        try:
            cmd_func(args)
        except SystemExit:
            print(f"\nPipeline stopped at: {label}", file=sys.stderr)
            sys.exit(1)

    print(f"\n{'=' * 50}")
    print(f"Pipeline complete! Knowledge base: {book_dir / 'knowledge_base.ml'}")
    print(f"Load it with: minilog repl {book_dir / 'knowledge_base.ml'}")


def _handle_extract(args) -> None:
    """Dispatch extract subcommands."""
    cmd_map = {
        "download": cmd_download,
        "detect-domains": cmd_detect_domains,
        "propose-schema": cmd_propose_schema,
        "extract-facts": cmd_extract_facts,
        "propose-rules": cmd_propose_rules,
        "generate-rules": cmd_generate_rules,
        "finalize": cmd_finalize,
        "run-all": cmd_run_all,
    }
    handler = cmd_map.get(args.extract_command)
    if handler:
        handler(args)
    else:
        print("Usage: minilog extract <download|detect-domains|propose-schema|extract-facts|propose-rules|generate-rules|finalize|run-all>")
        sys.exit(1)
