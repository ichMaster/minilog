# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

minilog is a mini-Prolog logic-programming engine with Ukrainian-language surface syntax. Stage 1 of a five-stage roadmap. It's a learning prototype, not a production tool.

The full technical specification lives in `specification/minilog-phase1-spec.md` — read it before starting any implementation task.

## Build & Run

```bash
python3.13 -m venv .venv                                    # create virtual environment (Python 3.13)
.venv/bin/pip install -e ".[dev]"                            # install in dev mode with test deps
.venv/bin/minilog version                                    # verify installation
.venv/bin/minilog run examples/family.ml                     # execute a .ml file
.venv/bin/minilog repl                                       # interactive shell
.venv/bin/minilog check examples/family.ml                   # parse-only syntax check
```

**Note for Claude Code:** Use `.venv/bin/python`, `.venv/bin/pytest`, `.venv/bin/pip`, `.venv/bin/minilog` directly instead of `source .venv/bin/activate` — the direct paths have pre-approved permissions.

## Testing

```bash
.venv/bin/pytest                                             # all tests
.venv/bin/pytest tests/unit/                                 # unit only
.venv/bin/pytest tests/integration/                          # integration only
.venv/bin/pytest tests/unit/test_engine.py                   # single file
.venv/bin/pytest tests/unit/test_engine.py::test_recursion   # single test
.venv/bin/pytest --cov=minilog --cov-report=term-missing     # with coverage
```

Coverage targets: 100% on `terms`, `unify`, `kb`, `engine`; 80%+ on `tracer`, `evolution`, `repl`, `cli`.

## Architecture

The pipeline is: `.ml` file → Lexer → Parser → KnowledgeBase + Queries → Engine → formatted output.

**Dependency layers (bottom-up, no cycles):**

1. **Foundation:** `terms.py` (frozen dataclasses: Atom, Var, Num, Str, Compound), `errors.py`
2. **Core logic:** `unify.py` (Robinson's algorithm, Substitution), `kb.py` (fact/rule storage indexed by functor/arity)
3. **Evaluation:** `evaluator.py` (arithmetic comparisons), `engine.py` (SLD backward chaining via generators), `forward.py` (saturation)
4. **Higher-level:** `tracer.py` (proof trees), `evolution.py` (production rules mutating KB)
5. **Frontend:** `lexer.py` → `parser.py` → `repl.py` / `cli.py`

**Key design invariants:**
- `solve()` returns `Iterator[Substitution]`, never a list — lazy evaluation throughout
- All Term types are frozen and hashable — they serve as dict keys and set members
- Variables are renamed with unique suffixes on each rule application to prevent collision
- Recursion bounded at depth 100 by default
- Negation-as-failure: `не G` succeeds iff `G` produces zero solutions

## Language Conventions

- **Python 3.11+**, stdlib only at runtime. `pytest`/`pytest-cov` are dev-only.
- Type hints on every public function and method.
- Pure functions for algorithms (`unify`, `solve`, `forward_chain`) — no side effects except explicit KB mutation in evolution.
- Error messages, docstrings, CLI output, and Python code are in **English**. The `.ml` syntax and `docs/language-reference.md` are in **Ukrainian**.
- Ukrainian keywords: `факт`, `правило`, `якщо`, `і`, `не`, `слід`. Variables use `?` prefix (`?х`, `?хто`, `?_`).

## Allowed Tools & Commands

Claude Code has pre-approved permissions for this project. No confirmation needed for:

- **Python:** `python3`, `python3.13`, `python`, `pip`, `pip3` (all subcommands)
- **Virtual env (direct paths):** `.venv/bin/python`, `.venv/bin/pytest`, `.venv/bin/pip`, `.venv/bin/minilog`
- **Testing:** `pytest` (all forms: single test, single file, coverage, unit/integration)
- **minilog CLI:** `minilog run`, `minilog repl`, `minilog check`, `minilog version`
- **Git:** all `git` subcommands (`status`, `log`, `diff`, `add`, `commit`, `push`, etc.)
- **GitHub CLI:** all `gh` subcommands (`issue`, `pr`, `repo`, `auth`, `api`)
- **GitHub MCP:** all issue, PR, branch, file, commit, and search operations
- **Filesystem:** `mkdir`, `ls`, `touch`, `wc`, `tree`, `cat`
- **Read/Write/Edit:** all files under this project
- **Glob/Grep:** all file search and content search under this project
- **TodoWrite:** task tracking for multi-step work
- **Skills:** `/execute-phase` (phase execution skill)

## Task Reference

Implementation is organized as MINILOG-001 through MINILOG-017 in the spec. Each task lists files, dependencies, and acceptance criteria. Follow the suggested execution order in section 11 of the spec.

GitHub issues are created at `ichMaster/minilog` (#1–#17), organized into 8 phases with cross-referenced dependencies.
