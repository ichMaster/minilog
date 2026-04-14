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


def _handle_extract(args) -> None:
    """Dispatch extract subcommands."""
    if args.extract_command == "download":
        cmd_download(args)
    else:
        print("Usage: minilog extract <download|detect-domains|propose-schema|extract-facts>")
        sys.exit(1)
