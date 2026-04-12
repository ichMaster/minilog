# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

minilog is a mini-Prolog logic-programming engine with Ukrainian-language surface syntax. Stage 1 of a five-stage roadmap. It's a learning prototype, not a production tool.

The full technical specification lives in `specification/minilog-phase1-spec.md` — read it before starting any implementation task.

## Build & Run

```bash
pip install -e .                    # install in dev mode
minilog version                     # verify installation
minilog run examples/family.ml      # execute a .ml file
minilog repl                        # interactive shell
minilog check examples/family.ml    # parse-only syntax check
```

## Testing

```bash
pytest                                            # all tests
pytest tests/unit/                                # unit only
pytest tests/integration/                         # integration only
pytest tests/unit/test_engine.py                  # single file
pytest tests/unit/test_engine.py::test_recursion  # single test
pytest --cov=minilog --cov-report=term-missing    # with coverage
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

- **Python:** `python3`, `python3.13`, `pip install`, `pip install -e .`
- **Testing:** `pytest` (all forms: single test, single file, coverage, unit/integration)
- **minilog CLI:** `minilog run`, `minilog repl`, `minilog check`, `minilog version`
- **Git:** `status`, `log`, `diff`, `add`, `commit`, `push`, `pull`, `fetch`, `branch`, `checkout`, `switch`, `merge`, `stash`, `remote`, `rm`, `mv`, `tag`, `rebase`
- **GitHub CLI:** `gh issue`, `gh pr`, `gh repo`, `gh auth`, `gh api`
- **GitHub MCP:** all issue, PR, branch, file, commit, and search operations
- **Filesystem:** `mkdir`, `ls`, `touch`, `wc`, `tree`
- **Read:** all files under this project

## Task Reference

Implementation is organized as MINILOG-001 through MINILOG-017 in the spec. Each task lists files, dependencies, and acceptance criteria. Follow the suggested execution order in section 11 of the spec.

GitHub issues are created at `ichMaster/minilog` (#1–#17), organized into 8 phases with cross-referenced dependencies.
