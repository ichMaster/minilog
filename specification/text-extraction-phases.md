# minilog Text Extraction — GitHub Issues Plan

## Issues Summary Table

| # | ID | Title | Size | Phase | Dependencies |
|---|---|---|---|---|---|
| 29 | MINILOG-029 | Downloader core and `extract` CLI skeleton | M | 11 — Downloader | MINILOG-013 |
| 30 | MINILOG-030 | HTML source handling via trafilatura | M | 11 — Downloader | MINILOG-029 |
| 31 | MINILOG-031 | PDF source handling via pymupdf4llm | M | 11 — Downloader | MINILOG-029 |
| 32 | MINILOG-032 | DOCX, EPUB, TXT, HTML-file, MD source handling | M | 11 — Downloader | MINILOG-029 |
| 33 | MINILOG-033 | Multi-source merging and metadata.txt | S | 11 — Downloader | MINILOG-030, MINILOG-031, MINILOG-032 |
| 34 | MINILOG-034 | Error handling and rollback | S | 11 — Downloader | MINILOG-033 |
| 35 | MINILOG-035 | Downloader documentation | S | 11 — Downloader | MINILOG-034 |
| 36 | MINILOG-036 | Built-in domain catalog | M | 12 — Schema Discovery | MINILOG-035 |
| 37 | MINILOG-037 | LLM bridge for Anthropic API | M | 12 — Schema Discovery | MINILOG-029 |
| 38 | MINILOG-038 | Session state management | S | 12 — Schema Discovery | MINILOG-029 |
| 39 | MINILOG-039 | Step 1: detect-domains implementation | M | 12 — Schema Discovery | MINILOG-036, MINILOG-037, MINILOG-038 |
| 40 | MINILOG-040 | Step 2a: propose predicates per domain | M | 12 — Schema Discovery | MINILOG-039 |
| 41 | MINILOG-041 | Step 2b: grounding check against text | M | 12 — Schema Discovery | MINILOG-040 |
| 42 | MINILOG-042 | domains.md generation and updates | S | 12 — Schema Discovery | MINILOG-039, MINILOG-041 |
| 43 | MINILOG-043 | CLI commands detect-domains and propose-schema | S | 12 — Schema Discovery | MINILOG-041, MINILOG-042 |
| 44 | MINILOG-044 | Phase 12 documentation | S | 12 — Schema Discovery | MINILOG-043 |
| 45 | MINILOG-045 | Facts extraction prompt engineering | M | 13 — Facts Extraction | MINILOG-043 |
| 46 | MINILOG-046 | Chunking for large texts | M | 13 — Facts Extraction | MINILOG-045 |
| 47 | MINILOG-047 | Facts file format with citations | S | 13 — Facts Extraction | MINILOG-045 |
| 48 | MINILOG-048 | Facts validation against schema and source | M | 13 — Facts Extraction | MINILOG-047 |
| 49 | MINILOG-049 | CLI command extract-facts | S | 13 — Facts Extraction | MINILOG-046, MINILOG-048 |
| 50 | MINILOG-050 | Phase 13 documentation | S | 13 — Facts Extraction | MINILOG-049 |
| 51 | MINILOG-051 | Rule proposals prompt engineering | M | 14 — Rules Induction | MINILOG-049 |
| 52 | MINILOG-052 | Rule body generation | M | 14 — Rules Induction | MINILOG-051 |
| 53 | MINILOG-053 | Rule validation: syntax and predicate references | M | 14 — Rules Induction | MINILOG-052 |
| 54 | MINILOG-054 | CLI commands propose-rules and generate-rules | S | 14 — Rules Induction | MINILOG-053 |
| 55 | MINILOG-055 | Finalize command: merge into knowledge_base.ml | S | 14 — Rules Induction | MINILOG-054 |
| 56 | MINILOG-056 | domains.md ontological profile update | S | 14 — Rules Induction | MINILOG-055 |
| 57 | MINILOG-057 | Phase 14 documentation | S | 14 — Rules Induction | MINILOG-056 |

**Size legend:** S = ≤ 0.5 day, M = 0.5–1 day, L = 1–2 days

---

## Locked Architectural Decisions

| Decision | Choice |
|---|---|
| Workflow interface | Batch mode with session files (each step is a separate CLI command) |
| LLM provider for MVP | Anthropic API (Claude) |
| Text languages supported | Ukrainian and English |
| Text size for MVP | Up to ~100K tokens |
| Facts with citations | Mandatory (hallucination defense) |
| Predicate grounding | Required on Step 2 |
| Built-in domain catalog | Hybrid: ~25 presets plus LLM-suggested extensions |
| Module structure | `minilog/extract/` with role-based files; `steps/` uses step-numbered filenames |
| Result storage | One folder per book at `knowledge_bases/<name>/` |
| Downloader sources | URLs plus local files (PDF, DOCX, EPUB, TXT, HTML, MD) |
| HTML conversion | trafilatura (main-content extraction + Markdown) |
| PDF conversion | pymupdf4llm |
| Source storage | Original file + converted `.md` side-by-side in book folder |
| Multiple sources per book | One command → multiple sources → one book (merged `source.md`) |
| Source naming scheme | URL slug / original filename |
| Source-vs-file detection | Automatic by `http://` / `https://` prefix |
| Download error policy | Entire command fails, folder is not created (rollback) |
| `source.md` merge format | Simple concatenation with `---` separator between sources |
| `metadata.txt` format | Plain `key: value` lines, UTF-8 |

---

## Phase 11 — Downloader

**Rationale:**
The text extraction workflow needs raw text to work on. Before any LLM-based processing (domain detection, schema proposal, fact extraction) can happen, the system must accept a source — either a URL pointing to an article, a Wikipedia page, or a blog post, or a local file in one of the common document formats (PDF, DOCX, EPUB, TXT, HTML, MD) — and produce a normalized Markdown representation that every subsequent step can read without worrying about the original format.

Phase 11 is the foundation of the entire text extraction pipeline. It establishes the book folder layout (`knowledge_bases/<name>/`), introduces the `minilog extract` CLI subcommand family, and implements one concrete command — `download` — that accepts one or more sources, fetches and converts them, and leaves a ready-to-process book folder on disk. No LLM calls happen in Phase 11; this phase is purely about I/O, format conversion, and folder bookkeeping.

After Phase 11, the user can run `minilog extract download --name anna_karenina --sources https://en.wikisource.org/wiki/Anna_Karenina,/path/to/notes.pdf` and get a folder containing the originals, their Markdown conversions, a merged `source.md`, and a `metadata.txt` file. That folder is then the input for Phase 12.

### MINILOG-029 — Downloader core and `extract` CLI skeleton

**Description:**
Introduce the `minilog extract` CLI subcommand family and implement the scaffolding that all downloader subcommands will share: argument parsing, book folder creation, source type detection (URL vs local file), and a dispatch mechanism that routes each source to the appropriate converter implemented in later issues.

**What needs to be done:**
- Create module `minilog/extract/__init__.py` (empty, marks the package)
- Create module `minilog/extract/cli.py` with the `extract` subcommand entry point
- Register `extract` as a subcommand of the main `minilog` CLI in `minilog/cli.py` (small, additive change — no existing commands modified)
- Implement `minilog extract download` subcommand with these arguments:
  - `--name <n>` (required): book folder name
  - `--sources <comma-separated-list>` (required): one or more sources
  - `--title <string>` (optional): override auto-detected title
  - `--author <string>` (optional): override auto-detected author
  - `--language <code>` (optional): override auto-detected language
- Parse `--sources` by splitting on commas; for each source, classify as URL (starts with `http://` or `https://`) or local file (everything else)
- Resolve the book folder path: read `MINILOG_KB_DIR` environment variable if set, otherwise default to `<project_root>/knowledge_bases/`. Target folder = `<kb_dir>/<n>/`
- Fail with a clear error if the target folder already exists (no overwriting)
- Create the folder (does not yet create any contents — that's the job of subsequent issues)
- Implement a dispatch stub: for each source, call into a converter module selected by type. In this issue the converter modules are not yet implemented, so the dispatch stub just prints what it would do ("would convert HTML source: https://...") and exits with success. Actual conversion lands in MINILOG-030..032
- Write ≥5 unit tests in `tests/unit/test_extract_cli.py`:
  - Invalid `--sources` (empty, malformed)
  - Existing folder causes failure
  - URL vs file classification works correctly
  - `MINILOG_KB_DIR` environment variable is respected
  - Dispatch routes each source type to the correct converter stub

**Dependencies:** MINILOG-013

**Expected result:**
A working `minilog extract download` command that validates inputs, creates the book folder, and correctly classifies each source by type, leaving the actual conversion to subsequent issues.

**Acceptance criteria:**
- [ ] `minilog extract download --help` prints the command signature
- [ ] `minilog extract download --name test --sources https://example.com/article,./notes.pdf` creates `knowledge_bases/test/` and prints the dispatch plan
- [ ] Running twice with the same `--name` fails with a clear error
- [ ] `MINILOG_KB_DIR=/tmp/kbs minilog extract download --name t --sources https://x.com` creates `/tmp/kbs/t/`
- [ ] 5+ unit tests passing
- [ ] No regression in existing CLI commands

---

### MINILOG-030 — HTML source handling via trafilatura

**Description:**
Implement HTML source conversion using the `trafilatura` library. Given a URL, fetch the page, extract the main article content (stripping navigation, ads, sidebars, comments), convert to Markdown, and save both the original HTML bytes and the converted Markdown into the book folder with an appropriate slug-based filename.

**What needs to be done:**
- Add `trafilatura` to project dependencies in `pyproject.toml`
- Create module `minilog/extract/converters/__init__.py`
- Create module `minilog/extract/converters/html_url.py` with function `download_html(url: str, target_dir: Path) -> ConversionResult`
- `ConversionResult` is a small dataclass with fields: `original_path`, `markdown_path`, `title`, `author`, `language`, `source_url`
- Slug generation: derive a filename slug from the URL (domain + cleaned path, limited to 80 chars, lowercase, non-alphanumerics replaced with `_`). Examples: `https://en.wikipedia.org/wiki/Prolog` → `en_wikipedia_org_wiki_prolog`, `https://blog.example.com/my-post/` → `blog_example_com_my_post`
- Save original HTML bytes to `<target_dir>/<slug>.html`
- Use trafilatura's extraction with `output_format='markdown'` to get the main content as Markdown
- Save converted Markdown to `<target_dir>/<slug>.md`
- Extract metadata from trafilatura's `extract_metadata()` output: title, author, language (if available)
- Handle errors gracefully: network timeout, 404, 403, invalid HTML, trafilatura failing to extract any content. All errors should raise a clear `DownloadError` with the URL and root cause
- Write ≥4 unit tests in `tests/unit/test_extract_html.py` using mocked HTTP responses:
  - Successful extraction from a clean article page
  - 404 response raises `DownloadError`
  - Page with no extractable content raises `DownloadError`
  - Slug generation works for various URL shapes

**Dependencies:** MINILOG-029

**Expected result:**
A reliable HTML downloader that produces clean Markdown from arbitrary web pages and stores both the original and the conversion in the book folder.

**Acceptance criteria:**
- [ ] `trafilatura` added as a dependency
- [ ] Downloading a real Wikipedia page produces readable Markdown with headings, paragraphs, and lists intact
- [ ] Navigation, sidebars, footers, and ad sections are excluded from the Markdown
- [ ] Both `<slug>.html` and `<slug>.md` exist in the book folder after success
- [ ] Errors raise `DownloadError` with informative messages
- [ ] 4+ unit tests passing

---

### MINILOG-031 — PDF source handling via pymupdf4llm

**Description:**
Implement PDF source conversion using the `pymupdf4llm` library, which is designed specifically to produce LLM-ready Markdown from PDF files with good handling of headings, paragraphs, tables, and basic formatting. Given a local PDF file path, convert it to Markdown and save both the original and the conversion in the book folder.

**What needs to be done:**
- Add `pymupdf4llm` to project dependencies in `pyproject.toml`
- Create module `minilog/extract/converters/pdf_file.py` with function `convert_pdf(path: Path, target_dir: Path) -> ConversionResult`
- Slug generation: use the original filename without extension, cleaned to lowercase alphanumerics and underscores, limited to 80 chars. Example: `Anna_Karenina_Vol1.pdf` → `anna_karenina_vol1`
- Copy the original PDF to `<target_dir>/<slug>.pdf`
- Call `pymupdf4llm.to_markdown(path)` to get the Markdown content
- Save converted Markdown to `<target_dir>/<slug>.md`
- Extract metadata from PyMuPDF's document metadata: title, author, language (if available in the PDF metadata dictionary)
- Handle errors: file not found, file is not a valid PDF, file is encrypted/password-protected, conversion produced empty output. All errors raise `DownloadError`
- Write ≥4 unit tests in `tests/unit/test_extract_pdf.py`:
  - Successful conversion of a small fixture PDF
  - Missing file raises `DownloadError`
  - Password-protected PDF raises `DownloadError` with a clear message
  - Slug generation works for various filename shapes

**Dependencies:** MINILOG-029

**Expected result:**
A reliable PDF converter that produces clean Markdown from scientific papers and books, storing both the original file and the conversion in the book folder.

**Acceptance criteria:**
- [ ] `pymupdf4llm` added as a dependency
- [ ] Converting a sample scientific paper produces Markdown with recognizable section headings
- [ ] Converting a sample book chapter produces paragraph-level Markdown
- [ ] Original PDF is copied into the book folder
- [ ] Errors raise `DownloadError` with informative messages
- [ ] 4+ unit tests passing

---

### MINILOG-032 — DOCX, EPUB, TXT, HTML-file, MD source handling

**Description:**
Implement converters for the remaining local file formats: DOCX (Microsoft Word), EPUB (e-books), TXT (plain text), HTML files (saved web pages), and MD (already Markdown). Each converter lives in its own module under `minilog/extract/converters/`, follows the same `ConversionResult` contract, and is routed by the CLI dispatcher based on file extension.

**What needs to be done:**
- Add dependencies: `python-docx` (DOCX), `ebooklib` (EPUB), `beautifulsoup4` (local HTML parsing)
- Create module `minilog/extract/converters/docx_file.py`:
  - Function `convert_docx(path, target_dir) -> ConversionResult`
  - Use `python-docx` to iterate paragraphs and headings, produce Markdown (headings from Word styles, paragraphs as plain text, bold/italic preserved where possible)
  - Copy original to `<slug>.docx`, save Markdown to `<slug>.md`
- Create module `minilog/extract/converters/epub_file.py`:
  - Function `convert_epub(path, target_dir) -> ConversionResult`
  - Use `ebooklib` to read chapters, convert each chapter's XHTML to Markdown (via trafilatura or beautifulsoup + simple rules), concatenate chapters with `## Chapter N` headings
  - Copy original to `<slug>.epub`, save Markdown to `<slug>.md`
  - Extract metadata from EPUB's OPF file: title, author, language
- Create module `minilog/extract/converters/text_file.py`:
  - Function `convert_txt(path, target_dir) -> ConversionResult` — plain text, minimal processing (copy to `<slug>.txt`, save as `<slug>.md` with no transformation beyond UTF-8 decoding)
  - Function `convert_md(path, target_dir) -> ConversionResult` — already Markdown, copy both original and `<slug>.md` (they are the same content)
- Create module `minilog/extract/converters/html_file.py`:
  - Function `convert_html_file(path, target_dir) -> ConversionResult`
  - Read the local HTML file, run it through trafilatura (same as MINILOG-030 but for local files instead of URLs)
  - Copy original to `<slug>.html`, save Markdown to `<slug>.md`
- Update the dispatcher in `minilog/extract/cli.py` from MINILOG-029 to route each source by file extension: `.pdf`→pdf converter, `.docx`→docx, `.epub`→epub, `.txt`→txt, `.md`→md, `.html`/`.htm`→html_file, URL→html_url
- Fail with `DownloadError` for unsupported extensions
- Write ≥2 unit tests per converter module (10+ total) in `tests/unit/test_extract_converters.py` using small fixture files

**Dependencies:** MINILOG-029

**Expected result:**
Complete coverage of the source formats promised by the downloader. Any of PDF, DOCX, EPUB, TXT, HTML (file or URL), or MD can be passed as a source.

**Acceptance criteria:**
- [ ] All six format converters implemented and dispatched correctly by file extension
- [ ] Fixture files for each format convert successfully and produce readable Markdown
- [ ] Unsupported extensions raise a clear `DownloadError`
- [ ] 10+ unit tests passing
- [ ] All new dependencies added to `pyproject.toml`

---

### MINILOG-033 — Multi-source merging and metadata.txt

**Description:**
When the `download` command receives multiple sources, each individual source is converted separately (by the per-format converters from MINILOG-030..032). This issue adds the final assembly step: merging all per-source Markdown files into a single `source.md` that subsequent workflow steps will read, and writing the `metadata.txt` file that describes the book at a high level.

**What needs to be done:**
- Create module `minilog/extract/merge.py` with function `merge_sources(results: list[ConversionResult], target_dir: Path) -> None`
- Merge format: simple concatenation with `---` separator on its own line between sources. Each source's content is preceded by a small header comment with the source identifier (URL or original filename) so that users reading `source.md` can see where each chunk came from
- Write the merged content to `<target_dir>/source.md`
- Create module `minilog/extract/metadata.py` with function `write_metadata(target_dir, name, results, overrides) -> None`
- `metadata.txt` format: plain `key: value` lines, UTF-8. Fields: name, title, author, sources (comma-separated), language, created_at (ISO 8601), model (empty for Phase 11 — filled in Phase 12)
- Auto-detect logic: title from the first source that provided one, author same pattern, language via `langdetect` on a sample of the merged Markdown if no converter provided one. All three auto-detections are overridable via the `--title`, `--author`, `--language` CLI flags from MINILOG-029
- `sources` field stores a comma-separated list of URLs and file paths exactly as entered by the user
- Add `langdetect` to project dependencies
- Write ≥3 unit tests in `tests/unit/test_extract_merge.py`:
  - Single source merge produces correct `source.md` layout
  - Multiple sources merge with correct `---` separators and source header comments
  - Metadata auto-detection falls back to overrides when the user provides them

**Dependencies:** MINILOG-030, MINILOG-031, MINILOG-032

**Expected result:**
After `download` completes, the book folder contains a ready-to-use `source.md` with all sources merged, and a `metadata.txt` that describes the book at a high level. Subsequent workflow steps can read `source.md` and `metadata.txt` without needing to know anything about the original source formats.

**Acceptance criteria:**
- [ ] `source.md` exists and contains all source contents with `---` separators between them
- [ ] Each chunk in `source.md` has a source identifier header comment
- [ ] `metadata.txt` contains all required fields in the specified format
- [ ] Auto-detection works when converters provide metadata, overrides work when CLI flags are passed
- [ ] 3+ unit tests passing
- [ ] `langdetect` added as a dependency

---

### MINILOG-034 — Error handling and rollback

**Description:**
Make the downloader atomic: if any source fails to download or convert, the entire command must fail and leave no partial book folder behind. This matches the locked design decision ("Download errors: entire command fails, folder is not created") and prevents the user from being left with a half-populated folder that later steps cannot process correctly.

**What needs to be done:**
- Refactor the `download` command flow so that source conversion happens before the book folder is finalized:
  - Create the book folder early (needed for per-source files to be written during conversion), but track all writes so they can be rolled back
  - If any converter raises `DownloadError`, catch it, delete the partially populated book folder, re-raise with a clear error message that identifies which source failed and why
  - Only after all sources converted successfully, proceed to merge (MINILOG-033) and metadata writing
- Improve error messages across all converters to include: the source identifier (URL or file path), the root cause (HTTP status, file-not-found, parse error, empty content, etc.), and a hint about what the user can check
- Add a top-level `DownloadError` class in `minilog/extract/errors.py` inheriting from `MinilogError`
- Ensure rollback is safe even if the folder was created earlier by the user (only delete files and subdirectories that the downloader itself created — use an internal tracking set)
- Write ≥4 unit tests in `tests/unit/test_extract_rollback.py`:
  - Failure on first source deletes folder
  - Failure on second source (after first succeeded) deletes folder including first source's files
  - Rollback does not delete pre-existing unrelated files if the folder was somehow non-empty
  - Error message contains source identifier and root cause

**Dependencies:** MINILOG-033

**Expected result:**
Failed downloads never leave partial state on disk. Users always see either a complete book folder or no folder at all, plus a clear error message.

**Acceptance criteria:**
- [ ] All converter errors propagate through `DownloadError` with informative messages
- [ ] Failure mid-download removes the book folder entirely
- [ ] Rollback is confined to files the downloader created
- [ ] 4+ unit tests passing
- [ ] No regressions in successful-path tests from MINILOG-030..033

---

### MINILOG-035 — Downloader documentation

**Description:**
Document the downloader in a dedicated document under `docs/` and cross-link from `language-reference.md` and README. This is the user-facing face of Phase 11 and must be clear enough that a new user can run their first download without asking questions.

**What needs to be done:**
- Create `docs/text-extraction.md` (Ukrainian main text, English technical terms, no emoji). Content structure:
  - Introduction: what `minilog extract` is, the overall workflow after Phase 12-14 are added, and what specifically works in Phase 11
  - The `minilog extract download` command: full syntax with all flags
  - Supported sources: list of formats with explanations, examples for each
  - Book folder structure after `download`: what `source.md` is, what `metadata.txt` is, where originals are stored
  - Working with multiple sources: how they are merged, what the separator shows, how language and title are picked
  - Common errors and how to resolve them: 404, corrupted PDF, wrong encoding, empty trafilatura output
  - Full end-to-end example: download a Wikipedia article and a local PDF into one book, inspect the result
- Update `docs/language-reference.md`: add a new short section "Text Extraction" at the end with a one-paragraph summary and a link to `text-extraction.md`
- Update `README.md`: add `minilog extract download` to the feature list and link to `docs/text-extraction.md`
- Add `knowledge_bases/` to the project `.gitignore` (book folders are user data, not source code)
- No new code — purely documentation

**Dependencies:** MINILOG-034

**Expected result:**
Complete, discoverable user documentation for the Phase 11 downloader, following the existing style of `language-reference.md` and `prolog-state-2025.md`.

**Acceptance criteria:**
- [ ] `docs/text-extraction.md` exists and covers all listed sections
- [ ] Document is in Ukrainian with English technical terms, no emoji
- [ ] `language-reference.md` cross-links to the new document
- [ ] `README.md` mentions `minilog extract download`
- [ ] `.gitignore` excludes `knowledge_bases/`
- [ ] No broken links

---

**Phase 11 scope notes:**

- Total effort: ~4-5 days (4 × M + 3 × S)
- Strictly sequential by dependency chain: MINILOG-029 is the foundation; MINILOG-030/031/032 can be done in parallel once 029 is merged; MINILOG-033/034/035 follow in order
- New external dependencies: `trafilatura`, `pymupdf4llm`, `python-docx`, `ebooklib`, `beautifulsoup4`, `langdetect`
- New modules created: `minilog/extract/` (package), `minilog/extract/cli.py`, `minilog/extract/converters/` (package with six modules), `minilog/extract/merge.py`, `minilog/extract/metadata.py`, `minilog/extract/errors.py`
- Existing files modified: `minilog/cli.py` (add `extract` subcommand), `pyproject.toml` (new dependencies), `.gitignore` (exclude `knowledge_bases/`), `README.md` and `docs/language-reference.md` (cross-links)
- New project folder: `knowledge_bases/` (user data, git-ignored)
- No changes to existing minilog modules (`terms.py`, `lexer.py`, `parser.py`, `kb.py`, `engine.py`, `evaluator.py`, `forward.py`, `evolution.py`, `tracer.py`, `repl.py`)
- Phase 11 introduces zero LLM calls. All LLM-based work is in Phase 12 and later.

**Acceptance for Phase 11 as a whole:**
Running `minilog extract download --name test_prolog --sources https://en.wikipedia.org/wiki/Prolog` produces a folder `knowledge_bases/test_prolog/` containing `en_wikipedia_org_wiki_prolog.html`, `en_wikipedia_org_wiki_prolog.md`, `source.md`, and `metadata.txt`. Running the same command again fails cleanly (folder exists). Running with a non-existent local file fails and does not create the folder.

---

## Phase 12 — Schema Discovery

**Rationale:**
With Phase 11 delivering a clean `source.md` in every book folder, Phase 12 introduces the first two LLM-powered steps of the extraction workflow: detecting which knowledge domains are present in the text (Step 1) and proposing a schema of minilog predicates for the selected domains with a grounding check against the actual text (Step 2).

This phase is where the interactive nature of the workflow becomes visible. The user does not get a fully automated pipeline; they get a sequence of LLM-generated proposals that they review, edit, and approve. Phase 12 produces the `schema.ml` file that Phase 13 will use to extract facts, and the `domains.md` document that records which domains were considered, which were selected, and what the grounding check revealed.

Phase 12 issues are captured at a high level below. Each issue will be expanded to full Description / What needs to be done / Acceptance criteria format as Phase 12 approaches implementation.

### MINILOG-036 — Built-in domain catalog

**Summary:** Create `minilog/extract/domains.py` containing a curated list of ~25 common knowledge domains (family, geography, biology, chemistry, military history, economics, medicine, literature, mythology, programming, etc.) each with a short description and a list of typical predicates. This catalog serves as the grounding reference for LLM domain suggestions on Step 1 and as the seed for schema proposals on Step 2. Hybrid model: LLM can propose domains outside the catalog if the text warrants it.

**Size:** M **Dependencies:** MINILOG-035

### MINILOG-037 — LLM bridge for Anthropic API

**Summary:** Create `minilog/extract/llm.py` — a thin wrapper around the `anthropic` Python SDK that handles API authentication (via `ANTHROPIC_API_KEY` environment variable), model selection (default `claude-opus-4-6`), retry logic, and response parsing. All subsequent LLM-using steps call into this module. No prompt logic here; prompts live in the step modules.

**Size:** M **Dependencies:** MINILOG-029

### MINILOG-038 — Session state management

**Summary:** Create `minilog/extract/session.py` — load and save the state of an extraction session (which step is next, what artifacts exist in the book folder, what the user has approved so far). Enables workflow resume across command invocations. State stored as simple JSON in `<book_folder>/.session.json`.

**Size:** S **Dependencies:** MINILOG-029

### MINILOG-039 — Step 1: detect-domains implementation

**Summary:** Implement `minilog/extract/steps/step1_detect_domains.py` — reads `source.md`, calls the LLM with a prompt that asks it to identify which domains from the built-in catalog (and which novel domains) are present in the text, with a brief justification for each. Output: list of detected domains with relevance scores and example passages. The user selects which detected domains to keep.

**Size:** M **Dependencies:** MINILOG-036, MINILOG-037, MINILOG-038

### MINILOG-040 — Step 2a: propose predicates per domain

**Summary:** Implement `minilog/extract/steps/step2_propose_schema.py` (first half) — for each user-selected domain, call the LLM with a prompt that asks it to propose minilog predicates (with arities and argument roles) that fit the domain. The proposal is knowledge-based — what the LLM knows about the domain, not yet checked against the text. Output: per-domain predicate list grouped by domain.

**Size:** M **Dependencies:** MINILOG-039

### MINILOG-041 — Step 2b: grounding check against text

**Summary:** Extend `step2_propose_schema.py` with the grounding pass — for each proposed predicate, ask the LLM to find 2-3 concrete examples in the text where that predicate applies (with citations). Predicates with no text examples are marked as "theoretical" (kept in the list but flagged). Predicates with examples are marked as "grounded". Output: annotated schema that the user can review.

**Size:** M **Dependencies:** MINILOG-040

### MINILOG-042 — domains.md generation and updates

**Summary:** Create the `domains.md` document in the book folder. Written initially after Step 1 (list of detected and selected domains with justifications), updated after Step 2 (adding grounding statistics per domain), and will be finalized in Phase 14 with an ontological profile. Markdown format following the style of `prolog-state-2025.md`.

**Size:** S **Dependencies:** MINILOG-039, MINILOG-041

### MINILOG-043 — CLI commands detect-domains and propose-schema

**Summary:** Add two new subcommands: `minilog extract detect-domains --name <n>` (runs Step 1) and `minilog extract propose-schema --name <n>` (runs Step 2a + Step 2b). Each command reads the book folder, runs the appropriate step, writes intermediate artifacts, and prints a summary for the user to review before proceeding.

**Size:** S **Dependencies:** MINILOG-041, MINILOG-042

### MINILOG-044 — Phase 12 documentation

**Summary:** Extend `docs/text-extraction.md` with sections on Steps 1 and 2: how `detect-domains` and `propose-schema` work, what the user sees, how to edit `domains.md` and `schema.ml` between steps, how grounding flags affect decisions.

**Size:** S **Dependencies:** MINILOG-043

**Phase 12 scope notes:**
- Total effort: ~6-7 days (5 × M + 4 × S)
- Dependency on Phase 11: must be fully merged
- New external dependency: `anthropic` Python SDK
- Introduces the first LLM calls in the entire minilog project
- Phase 12 acceptance: after running `download` → `detect-domains` → (user selects) → `propose-schema` → (user approves), the book folder contains a finalized `schema.ml` and a `domains.md` with grounding statistics

---

## Phase 13 — Facts Extraction

**Rationale:**
With an approved schema in place, Phase 13 implements Step 3 of the workflow: the LLM reads the full `source.md` and extracts concrete ground facts that match the schema, each annotated with a citation from the source text. This is the step that actually turns a text into a loadable minilog knowledge base.

Phase 13 adds one new CLI command, handles the tension between text length and LLM context window (chunking for large texts), validates every extracted fact against both the schema and the source (the citation must actually exist in the text), and produces a `facts.ml` file that is ready to be loaded into the minilog REPL for querying.

### MINILOG-045 — Facts extraction prompt engineering

**Summary:** Design and implement the LLM prompt for Step 3. The prompt receives the approved schema and a chunk of source text, and asks the LLM to return all ground facts from the text that match any predicate in the schema, each with a citation (short quoted passage). Multiple iterations may be needed to find a prompt that balances recall (don't miss facts) against precision (don't hallucinate facts not in the text).

**Size:** M **Dependencies:** MINILOG-043

### MINILOG-046 — Chunking for large texts

**Summary:** For texts longer than ~50K tokens, split into overlapping chunks before sending to the LLM. Each chunk is processed independently; facts are then merged and deduplicated across chunks. Deduplication is based on exact structural match of the Compound term. Size limit is configurable; default chosen to stay safely within Claude Opus context window while leaving room for the schema and the response.

**Size:** M **Dependencies:** MINILOG-045

### MINILOG-047 — Facts file format with citations

**Summary:** Define the format of `facts.ml`: each fact on its own line, followed by a comment with the citation (short quoted passage from the source). The file is valid minilog (comments are ignored by the parser), but human readers see the provenance of every fact. Also specify the layout: facts grouped by predicate, predicates grouped by domain.

**Size:** S **Dependencies:** MINILOG-045

### MINILOG-048 — Facts validation against schema and source

**Summary:** Implement validation pass after extraction: every fact must (a) use a predicate that exists in the schema with the correct arity, (b) have argument types consistent with the schema's argument role hints, and (c) have a citation string that is a substring of `source.md` (modulo whitespace normalization). Facts that fail validation are flagged and presented to the user for manual review, not silently dropped.

**Size:** M **Dependencies:** MINILOG-047

### MINILOG-049 — CLI command extract-facts

**Summary:** Add `minilog extract extract-facts --name <n>` subcommand. Reads the book folder, checks that `schema.ml` exists and is approved, runs the extraction pass (with chunking if needed), runs validation, writes `facts.ml`, prints a summary (number of facts per predicate, any validation warnings).

**Size:** S **Dependencies:** MINILOG-046, MINILOG-048

### MINILOG-050 — Phase 13 documentation

**Summary:** Extend `docs/text-extraction.md` with a section on Step 3: how `extract-facts` works, how citations help detect hallucinations, how to review and edit `facts.ml` before moving on to Phase 14.

**Size:** S **Dependencies:** MINILOG-049

**Phase 13 scope notes:**
- Total effort: ~4-5 days (4 × M + 2 × S)
- Dependency on Phase 12: must be fully merged
- No new external dependencies beyond what Phase 12 introduced
- Phase 13 acceptance: after running `extract-facts`, the book folder contains a validated `facts.ml` with citations, and the file can be loaded into the minilog REPL with `:load knowledge_bases/<n>/facts.ml` and queried

---

## Phase 14 — Rules Induction

**Rationale:**
The last two steps of the workflow (Steps 4 and 5) are the rule induction phase. Given the text, the selected domains, and the extracted facts, the LLM proposes candidate rules that would be natural additions to the knowledge base, and then — for each rule the user selects — generates a concrete rule body in minilog syntax that the user can edit before committing. This is LLM-assisted rule induction: the LLM plays the role of a domain expert suggesting useful patterns, and the user decides what goes into the final base.

Phase 14 closes the workflow: after it completes, the book folder contains a fully assembled `knowledge_base.ml` that combines schema, facts, and rules, plus a finalized `domains.md` with an "ontological profile" summarizing what the base captures.

### MINILOG-051 — Rule proposals prompt engineering

**Summary:** Design the LLM prompt for Step 4. Inputs: domain descriptions, extracted facts, the source text. Output: a list of candidate rules grouped by domain, each with a short natural-language description of what the rule captures and why it would be useful. No code bodies yet — these come in Step 5.

**Size:** M **Dependencies:** MINILOG-049

### MINILOG-052 — Rule body generation

**Summary:** Design the LLM prompt for Step 5. For each user-selected candidate rule from Step 4, ask the LLM to produce a concrete minilog rule body using the predicates from the approved schema. Output: fully-formed rule in `правило head якщо body.` syntax that the user can edit.

**Size:** M **Dependencies:** MINILOG-051

### MINILOG-053 — Rule validation: syntax and predicate references

**Summary:** After each generated rule body, run it through the minilog parser to check syntax, and check that every predicate referenced in the body is either defined in the schema or a known built-in (comparison operators, arithmetic functions). Invalid rules are flagged for user review, not silently dropped.

**Size:** M **Dependencies:** MINILOG-052

### MINILOG-054 — CLI commands propose-rules and generate-rules

**Summary:** Add two subcommands: `minilog extract propose-rules --name <n>` (runs Step 4) and `minilog extract generate-rules --name <n>` (runs Step 5 on user-selected rules from Step 4). Standard pattern: read book folder, check preconditions, run the step, write intermediate files, print a summary.

**Size:** S **Dependencies:** MINILOG-053

### MINILOG-055 — Finalize command: merge into knowledge_base.ml

**Summary:** Add `minilog extract finalize --name <n>` — merges `schema.ml`, `facts.ml`, and `rules.ml` into a single `knowledge_base.ml` file that can be loaded into the minilog REPL as a complete base. Adds a file header comment documenting provenance (sources, extraction date, model used, workflow version).

**Size:** S **Dependencies:** MINILOG-054

### MINILOG-056 — domains.md ontological profile update

**Summary:** Extend `domains.md` with a final section written after `finalize` — an "ontological profile" summarizing what the knowledge base captures: number of facts per domain, number of rules per domain, cross-domain links (predicates shared between domains), coverage gaps (grounded predicates with zero extracted facts). This closes the `domains.md` lifecycle started in Phase 12.

**Size:** S **Dependencies:** MINILOG-055

### MINILOG-057 — Phase 14 documentation

**Summary:** Extend `docs/text-extraction.md` with sections on Steps 4 and 5 and the finalize step. Include a complete end-to-end example: downloading a real article, running all five workflow steps, and querying the resulting knowledge base in the REPL.

**Size:** S **Dependencies:** MINILOG-056

**Phase 14 scope notes:**
- Total effort: ~5-6 days (4 × M + 3 × S)
- Dependency on Phase 13: must be fully merged
- Closes the extraction workflow — after Phase 14, the full pipeline from URL to queryable knowledge base is operational
- Phase 14 acceptance: running the full sequence (`download` → `detect-domains` → `propose-schema` → `extract-facts` → `propose-rules` → `generate-rules` → `finalize`) on a real Wikipedia article produces a `knowledge_base.ml` file that can be loaded into the REPL and queried, with `domains.md` showing the complete ontological profile of what was extracted

---

## Overall Estimate

| Phase | Issues | Effort | Deliverable |
|---|---|---|---|
| Phase 11 — Downloader | 7 | 4-5 days | Book folder with converted `source.md` |
| Phase 12 — Schema Discovery | 9 | 6-7 days | Approved `schema.ml` + annotated `domains.md` |
| Phase 13 — Facts Extraction | 6 | 4-5 days | Validated `facts.ml` with citations |
| Phase 14 — Rules Induction | 7 | 5-6 days | Complete `knowledge_base.ml` + finalized `domains.md` |
| **Total** | **29** | **~20 days** | Full text-to-knowledge-base pipeline |

---

**Document status:** draft for review. Phase 11 issues are fully detailed. Phases 12-14 are captured at high level (one-paragraph summaries per issue); they will be expanded to full Description / What needs to be done / Acceptance criteria format as each phase approaches implementation.

**No code changes made. Plan only.**
