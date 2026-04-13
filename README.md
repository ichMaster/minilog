# minilog

A mini-Prolog logic-programming engine with Ukrainian-language surface syntax.

minilog is a learning prototype that implements backward chaining (SLD resolution), forward chaining (saturation), proof-tree construction, and a production-rule evolution engine — all with Ukrainian keywords and identifiers.

## Installation

Requires **Python 3.11+** (developed with 3.13).

```bash
git clone https://github.com/ichMaster/minilog.git
cd minilog
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Verify the installation:

```bash
.venv/bin/minilog version
```

## Quickstart

Create a file `hello.ml`:

```
батько(авраам, ісак).
батько(ісак, яків).

правило предок(?x, ?y) якщо батько(?x, ?y).
правило предок(?x, ?z) якщо батько(?x, ?y) і предок(?y, ?z).

?- предок(авраам, ?хто).
```

Run it:

```bash
.venv/bin/minilog run hello.ml
```

Output:

```
?хто = ісак.
?хто = яків.
(2 solutions)
```

Or use the interactive REPL:

```bash
.venv/bin/minilog repl
```

```
minilog 0.1.0 — type :help for commands, :quit to exit
minilog> батько(авраам, ісак).
Added fact: батько(авраам, ісак).
minilog> ?- батько(?x, ісак).
?x = авраам.
(1 solution)
minilog> :quit
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `minilog run <file.ml>` | Load a file and execute all queries |
| `minilog repl [file.ml]` | Start the interactive shell |
| `minilog check <file.ml>` | Parse-only syntax check |
| `minilog version` | Print the version string |

## Examples

Nine example files are included in `examples/`:

| File | Description |
|------|-------------|
| `family.ml` | Biblical patriarchs — unification, recursion |
| `directions.ml` | Ukrainian cities — symmetric and transitive relations |
| `dwh_dependencies.ml` | Data warehouse — cycle and write-conflict detection |
| `biology.ml` | Taxonomy — inheritance, negation, proof trees |
| `recipes.ml` | Dishes — multi-layer negation (vegetarian/vegan) |
| `mythology.ml` | Slavic gods — cultural structure modeling |
| `causality.ml` | Weather/transport — transitive causation, common cause |
| `terra_tacita.ml` | Inter-species communication via artifacts |
| `biology_evolution.ml` | Production rules preserving formal rules |

Run any example:

```bash
.venv/bin/minilog run examples/biology.ml
```

## Testing

```bash
.venv/bin/pytest                                          # all tests
.venv/bin/pytest tests/unit/                              # unit only
.venv/bin/pytest tests/integration/                       # integration only
.venv/bin/pytest --cov=minilog --cov-report=term-missing  # with coverage
```

## Language Reference

The full language reference is written in Ukrainian:
**[docs/language-reference.md](docs/language-reference.md)**

Ukrainian keywords: `факт`, `правило`, `якщо`, `і`, `не`, `слід`. Variables use `?` prefix (`?х`, `?хто`, `?_`).

## Architecture

```
.ml file → Lexer → Parser → KnowledgeBase + Queries → Engine → Output
```

**Layers (bottom-up):**

1. **Foundation:** `terms.py`, `errors.py`
2. **Core logic:** `unify.py`, `kb.py`
3. **Evaluation:** `evaluator.py`, `engine.py`, `forward.py`
4. **Higher-level:** `tracer.py`, `evolution.py`
5. **Frontend:** `lexer.py`, `parser.py`, `repl.py`, `cli.py`

## Roadmap

minilog is Phase 1 of a five-phase research roadmap. Phase 1 includes the core engine (this current state), plus two planned extensions — a lightweight type system and a web interface — that will be added as part of the same implementation cycle before Phase 1 is considered complete. All five phases are tracked in Notion: *"Five Phases — Long-Term Research Roadmap"*.

| Phase | Name | Description |
|-------|------|-------------|
| **1** | **minilog** (this repo) | Core engine + types + web interface. Ukrainian syntax, 9 examples, proof trees, evolution engine. |
| 2 | codex-axioms | Formal axiomatic layer for Codex Seraphinianus analyzer |
| 3 | ca-evolution | Interpretable cellular-automata evolution via logical inference |
| 4 | migvisor-axioms | Architectural validation for DWH migration (commercial) |
| 5 | terra-tacita-canon | Canon keeper for the Terra Tacita SF trilogy |

The current state of this repo covers the core engine. Type declarations, modules, and the web interface are planned additions within Phase 1 and will land before Phase 2 begins.

## License

MIT
