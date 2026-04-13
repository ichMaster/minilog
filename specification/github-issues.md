# minilog Stage 1 — GitHub Issues Plan

## Issues Summary Table

| # | ID | Title | Size | Phase | Dependencies |
|---|---|---|---|---|---|
| 1 | MINILOG-001 | Project skeleton and packaging | S | 1 — Foundation | -- |
| 2 | MINILOG-002 | Term model | S | 1 — Foundation | MINILOG-001 |
| 3 | MINILOG-003 | Error hierarchy | S | 1 — Foundation | MINILOG-001 |
| 4 | MINILOG-004 | Lexer | M | 2 — Lexer & Parser | MINILOG-002, MINILOG-003 |
| 5 | MINILOG-005 | Parser | L | 2 — Lexer & Parser | MINILOG-004 |
| 6 | MINILOG-006 | Substitution and unification | M | 3 — Core Logic | MINILOG-002 |
| 7 | MINILOG-007 | Knowledge Base | S | 3 — Core Logic | MINILOG-005 |
| 8 | MINILOG-008 | Evaluator | S | 3 — Core Logic | MINILOG-006 |
| 9 | MINILOG-009 | Backward-chaining engine | L | 4 — Engine | MINILOG-006, MINILOG-007, MINILOG-008 |
| 10 | MINILOG-010 | Forward chaining | M | 5 — Advanced Engines | MINILOG-009 |
| 11 | MINILOG-011 | Tracer and proof trees | M | 5 — Advanced Engines | MINILOG-009 |
| 12 | MINILOG-012 | Evolution engine | M | 5 — Advanced Engines | MINILOG-010 |
| 13 | MINILOG-013 | CLI and REPL | L | 6 — Frontend | MINILOG-009, MINILOG-011 |
| 14 | MINILOG-014 | Examples: family, directions, dwh_dependencies | M | 7 — Examples | MINILOG-013 |
| 15 | MINILOG-015 | Examples: biology, recipes, mythology, causality, terra_tacita | M | 7 — Examples | MINILOG-014 |
| 16 | MINILOG-016 | Evolution example: biology_evolution | M | 7 — Examples | MINILOG-012, MINILOG-015 |
| 17 | MINILOG-017 | Documentation and polish | M | 8 — Documentation | MINILOG-013, MINILOG-014, MINILOG-015, MINILOG-016 |
| 18 | MINILOG-018 | KnowledgeBase.predicates() enumeration method | S | 9 — REPL Diagnostics | MINILOG-007 |
| 19 | MINILOG-019 | Enhanced `:stats` with per-predicate breakdown | S | 9 — REPL Diagnostics | MINILOG-018, MINILOG-013 |
| 20 | MINILOG-020 | New `:kb` command for full knowledge base dump | S | 9 — REPL Diagnostics | MINILOG-018, MINILOG-013 |
| 21 | MINILOG-021 | Lexer support for arithmetic operators and negative numbers | S | 9 — Arithmetic Expressions | MINILOG-004 |
| 22 | MINILOG-022 | Parser support for arithmetic expressions in comparison goals | M | 9 — Arithmetic Expressions | MINILOG-021, MINILOG-005 |
| 23 | MINILOG-023 | Evaluator support for compound arithmetic terms and built-in functions | M | 9 — Arithmetic Expressions | MINILOG-022, MINILOG-008 |
| 24 | MINILOG-024 | Arithmetic documentation, examples, and language reference update | S | 9 — Arithmetic Expressions | MINILOG-023 |
| 25 | MINILOG-025 | Geometry example: triangle classification and theorems (.ml file) | M | 10 — Geometry | MINILOG-023 |
| 26 | MINILOG-026 | Geometry example: expected output and integration test | S | 10 — Geometry | MINILOG-025 |
| 27 | MINILOG-027 | Geometry example: theoretical companion document | M | 10 — Geometry | MINILOG-025 |
| 28 | MINILOG-028 | Geometry example: language reference and README integration | S | 10 — Geometry | MINILOG-025, MINILOG-027 |

**Size legend:** S = ≤ 0.5 day, M = 0.5–1 day, L = 1–2 days

---

## Dependency Tree

```
                 MINILOG-001 (skeleton)
                      |
            +---------+---------+
            v         v         |
      MINILOG-002  MINILOG-003  |
      (terms)      (errors)     |
            |         |         |
            +----+----+         |
                 v              |
            MINILOG-004         |
              (lexer)           |
                 |              |
                 v              |
            MINILOG-005         |
             (parser)           |
                 |              |
      +----------+----------+  |
      v          v           |  |
 MINILOG-006 MINILOG-007     |  |
  (unify)      (kb)          |  |
      |          |           |  |
      +----+-----+           |  |
           v                 |  |
      MINILOG-008            |  |
      (evaluator)            |  |
           |                 |  |
           v                 |  |
      MINILOG-009            |  |
      (engine)               |  |
      +----+----------+      |  |
      v    v           v     |  |
MINILOG-010 MINILOG-011  |   |  |
 (forward)  (tracer)     |   |  |
      |         |        |   |  |
      v         |        |   |  |
MINILOG-012     |        |   |  |
(evolution)     |        |   |  |
      |         |        |   |  |
      +----+----+        |   |  |
           v             |   |  |
      MINILOG-013 <------+   |  |
      (cli + repl)           |  |
           |                 |  |
           v                 |  |
      MINILOG-014            |  |
  (examples 1-3 + tests)    |  |
           |                 |  |
           v                 |  |
      MINILOG-015            |  |
  (examples 4-8 + tests)    |  |
           |                 |  |
           v                 |  |
      MINILOG-016 <-- MINILOG-012
 (evolution example + test)  |  |
           |                 |  |
           v                 |  |
      MINILOG-017            |  |
  (docs and polish)          |  |
```

**Parallelization hints:**

- MINILOG-002 and MINILOG-003 can run in parallel after MINILOG-001
- MINILOG-006 and MINILOG-007 can run in parallel after MINILOG-005
- MINILOG-010 and MINILOG-011 can run in parallel after MINILOG-009; MINILOG-012 needs MINILOG-010
- Example tasks (MINILOG-014 → 015 → 016) must be sequential for regression stability

---

## Phase 1 — Foundation

### MINILOG-001 — Project skeleton and packaging

**Description:**
Set up the Python project layout and packaging infrastructure for minilog.

**What needs to be done:**
- Create `pyproject.toml` for Python 3.11+ with entry point `minilog = minilog.cli:main`
- Add `pytest` and `pytest-cov` as dev dependencies
- Create `minilog/__init__.py` (empty, will hold public exports later)
- Create `README.md` (minimal, just project name and one-liner)
- Create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`
- Create `examples/` (empty directory with `.gitkeep`)
- Create `docs/` (empty directory with `.gitkeep`)
- Ensure `pip install -e .` succeeds and `minilog version` can be invoked (even if it prints a placeholder)

**Dependencies:** None

**Expected result:**
A clean Python project skeleton that installs correctly and has a working (placeholder) CLI entry point.

**Acceptance criteria:**
- [ ] `pip install -e .` exits 0
- [ ] `python -c "import minilog"` succeeds
- [ ] `minilog version` prints something like `minilog 0.1.0`
- [ ] Directory layout matches section 3.1 of the specification

---

### MINILOG-002 — Term model

**Description:**
Implement the core value types for the minilog language as frozen, hashable dataclasses.

**What needs to be done:**
- Implement `Atom`, `Var`, `Num`, `Str`, `Compound` as frozen dataclasses in `minilog/terms.py`
- All types must be hashable (for use as dict keys and set members)
- Implement `__repr__` for each type to produce the expected surface form (e.g., `батько(авраам, ісак)`)
- Add `arity` property on `Compound`
- Implement module-level `is_ground(term) -> bool` that recursively checks for variables
- Write ≥5 unit tests in `tests/unit/test_terms.py`

**Dependencies:** MINILOG-001

**Expected result:**
A `terms.py` module providing the immutable data model that all other modules build upon.

**Acceptance criteria:**
- [ ] All term types instantiate and compare by value equality
- [ ] `hash(term)` works for every term type
- [ ] `repr(Compound("батько", (Atom("авраам"), Atom("ісак"))))` equals `"батько(авраам, ісак)"`
- [ ] `is_ground(Atom("x"))` is `True`; `is_ground(Var("y"))` is `False`; `is_ground(Compound("f", (Atom("a"), Var("b"))))` is `False`
- [ ] ≥5 unit tests, all passing

---

### MINILOG-003 — Error hierarchy

**Description:**
Create an error class hierarchy for all minilog-specific exceptions with optional source location information.

**What needs to be done:**
- Create `minilog/errors.py`
- Root class: `MinilogError`
- Subclasses: `LexError`, `ParseError`, `UnifyError`, `SolveError`, `EvaluatorError`
- Each error carries optional `line` and `col` fields for source context
- `__str__` produces English messages: `"{ErrorType} at line {L}, col {C}: {message}"`, gracefully omitting position info when not available

**Dependencies:** MINILOG-001

**Expected result:**
A consistent error hierarchy that all modules use for error reporting, with source position information where applicable.

**Acceptance criteria:**
- [ ] Each error type can be instantiated with `(message)`, `(line, col, message)`, or `(message=..., line=..., col=...)`
- [ ] `str(LexError(5, 12, "unexpected character '@'"))` equals `"LexError at line 5, col 12: unexpected character '@'"`
- [ ] `str(SolveError("predicate foo/2 not found"))` equals `"SolveError: predicate foo/2 not found"`

---

## Phase 2 — Lexer & Parser

### MINILOG-004 — Lexer

**Description:**
Implement the lexer that tokenizes Ukrainian-language minilog source code into a structured token stream.

**What needs to be done:**
- Implement `minilog/lexer.py` producing `list[Token]` from a source string
- Support Ukrainian keywords: `факт`, `правило`, `якщо`, `і`, `не`, `слід`
- Support variables: `?ident`, `?_`
- Support Unicode-aware identifiers (any `L*` category)
- Support numbers (int and float), string literals with `\n`, `\"`, `\\` escapes
- Support operators: `(`, `)`, `,`, `.`, `:`, `?-`, `≥`, `≤`, `>`, `<`, `=`, `≠`
- Support line comments `% ...`
- Emit `INDENT`/`DEDENT` for block-form rules, `NEWLINE` between statements
- Token fields: `type: TokenType`, `value: str`, `line: int`, `col: int`
- Raise `LexError` on unrecognized input
- Write ≥8 unit tests in `tests/unit/test_lexer.py`

**Dependencies:** MINILOG-002, MINILOG-003

**Expected result:**
A lexer that correctly tokenizes all valid minilog syntax including both inline and block rule forms.

**Acceptance criteria:**
- [ ] 8+ unit tests covering: simple facts, both rule forms, comments inside and between lines, Ukrainian-named variables, numbers, strings, malformed input
- [ ] `tokenize("батько(авраам, ісак).")` produces `[IDENT, LPAREN, IDENT, COMMA, IDENT, RPAREN, DOT, EOF]` with correct line/col
- [ ] Block-form input correctly produces `INDENT`/`DEDENT` pairs

---

### MINILOG-005 — Parser

**Description:**
Implement a recursive-descent parser that transforms the token stream into a Program AST.

**What needs to be done:**
- Implement `minilog/parser.py` consuming tokens from the lexer
- Handle facts, both inline and block rule forms, queries with and without `слід` prefix
- Handle negation goals (`не compound(...)`) and comparison goals (`term op term`)
- Handle nested compound terms
- Provide proper error reporting with line/col information
- Reject syntactically invalid input with `ParseError`
- Do NOT perform semantic validation (missing predicates, arity mismatches)
- Write ≥7 unit tests in `tests/unit/test_parser.py`

**Dependencies:** MINILOG-004

**Expected result:**
A parser that produces a correct AST for all valid minilog syntax and reports clear errors for invalid syntax.

**Acceptance criteria:**
- [ ] 7+ unit tests covering: single fact, inline rule, block rule, query, traced query, negation goal, comparison goal, syntax errors
- [ ] Parsing the grammar examples from spec section 4 produces the expected AST
- [ ] Error messages include line and column information

---

## Phase 3 — Core Logic

### MINILOG-006 — Substitution and unification

**Description:**
Implement Robinson's unification algorithm and the Substitution data type that underlies all inference.

**What needs to be done:**
- Implement `Substitution` in `minilog/unify.py` as a frozen, hashable data type
- Provide `empty()`, `extend(var, term)`, `lookup(var)`, and `apply(term)` operations
- Implement `walk(term, subst)` for variable dereferencing
- Implement `unify(t1, t2, subst) -> Substitution | None` following Robinson's algorithm
- Occurs check disabled by default
- Write ≥8 unit tests in `tests/unit/test_unify.py`

**Dependencies:** MINILOG-002

**Expected result:**
A correct unification implementation that produces substitutions for compatible terms and `None` for incompatible ones.

**Acceptance criteria:**
- [ ] 8+ unit tests covering: atom-atom success, atom-atom failure, var-binding, compound-compound success, compound-compound arity mismatch, nested unification, `walk` chain, `apply` round-trip
- [ ] `unify(Var("x"), Atom("a"), empty())` produces a substitution where `apply(Var("x"))` returns `Atom("a")`
- [ ] `unify(Compound("f", (Var("x"), Atom("b"))), Compound("f", (Atom("a"), Var("y"))), empty())` succeeds
- [ ] `unify(Compound("f", (Atom("a"),)), Compound("g", (Atom("a"),)), empty())` returns `None`

---

### MINILOG-007 — Knowledge Base

**Description:**
Implement the knowledge base that stores facts and rules indexed by predicate functor and arity.

**What needs to be done:**
- Implement `KnowledgeBase` in `minilog/kb.py`
- Provide `add_fact`, `add_rule`, `lookup(functor, arity)`, `remove_fact`, `all_facts`, and `stats` methods
- Facts and rules stored in separate dicts keyed by `(functor, arity)`
- Write ≥4 unit tests in `tests/unit/test_kb.py`

**Dependencies:** MINILOG-005

**Expected result:**
A knowledge base that efficiently stores and retrieves facts and rules by predicate signature.

**Acceptance criteria:**
- [ ] 4+ unit tests covering: add/lookup, multiple predicates, remove, stats
- [ ] `lookup` returns `([], [])` for unknown predicates (does not raise)
- [ ] Stats reports correct fact, rule, and predicate counts

---

### MINILOG-008 — Evaluator

**Description:**
Implement arithmetic evaluation and comparison operators for numeric terms.

**What needs to be done:**
- Implement `evaluate(term, subst) -> Num` in `minilog/evaluator.py` that resolves a term to a numeric value
- Raise `EvaluatorError` on non-numeric terms
- Implement `check_comparison(left, op, right, subst) -> bool` for `≥`, `≤`, `>`, `<`, `=`, `≠`
- `=` here is numeric equality only (unification equality is in `unify.py`)
- Write ≥3 unit tests in `tests/unit/test_evaluator.py`

**Dependencies:** MINILOG-006

**Expected result:**
An evaluator that correctly resolves numeric comparisons under substitutions and reports type errors clearly.

**Acceptance criteria:**
- [ ] 3+ unit tests covering arithmetic, comparisons, and non-numeric failure
- [ ] `check_comparison(Num(5), ">", Num(3), empty())` returns `True`
- [ ] Comparing a non-numeric term raises `EvaluatorError`

---

## Phase 4 — Engine

### MINILOG-009 — Backward-chaining engine

**Description:**
Implement the SLD resolution engine — the core inference mechanism that solves queries against the knowledge base.

**What needs to be done:**
- Implement `solve(goal, kb, subst, depth, max_depth)` in `minilog/engine.py` as a generator of substitutions
- Implement helper `solve_body(body, kb, subst, depth, max_depth)` for conjunctions
- Implement `rename_variables(rule, suffix)` to produce fresh-variable copies per rule application
- Handle: fact matching, rule application with fresh variables, body conjunction, comparison goals (delegated to evaluator), negation-as-failure, MAX_DEPTH guard raising `SolveError`, missing predicates raising `SolveError`
- Write ≥10 unit tests in `tests/unit/test_engine.py`

**Dependencies:** MINILOG-006, MINILOG-007, MINILOG-008

**Expected result:**
A lazy backward-chaining engine that streams solutions as an iterator, supporting recursion, negation, and comparisons.

**Acceptance criteria:**
- [ ] 10+ unit tests covering: single fact solve, single rule solve, recursive rule, multi-solution backtracking, negation success, negation failure, comparison goal, max-depth trip, missing predicate, body with multiple goals
- [ ] `solve` returns an iterator (not a list); solutions stream lazily

---

## Phase 5 — Advanced Engines

### MINILOG-010 — Forward chaining

**Description:**
Implement forward chaining (saturation) that derives all possible facts from existing rules until a fixpoint is reached.

**What needs to be done:**
- Implement `saturate(kb, max_iterations) -> int` in `minilog/forward.py`
- Repeatedly apply all rules in the KB, adding newly derivable ground facts
- Stop when no new facts are produced (fixpoint) or `max_iterations` is reached
- Use `solve_body` from the engine internally
- Deduplicate: a fact already in the KB is not added again
- Write ≥4 unit tests in `tests/unit/test_forward.py`

**Dependencies:** MINILOG-009

**Expected result:**
A saturation algorithm that correctly derives all implicit facts and detects fixpoints.

**Acceptance criteria:**
- [ ] 4+ unit tests covering: simple saturation, fixpoint detection, empty KB, no-op KB with no rules
- [ ] Running `saturate` twice in a row returns `>0` the first time and `0` the second time (idempotence at fixpoint)

---

### MINILOG-011 — Tracer and proof trees

**Description:**
Implement proof-tree construction and rendering for traced queries, providing visual explanations of how solutions are derived.

**What needs to be done:**
- Implement `ProofNode` dataclass in `minilog/tracer.py`
- Implement `Tracer.trace_solve(goal, kb, subst)` that mirrors `solve` structurally but also constructs a `ProofNode` tree for each successful derivation
- Implement `ProofNode.format_tree()` using Unicode box-drawing characters (`├─`, `└─`, `│`) to render the proof tree as a printable string
- Implement `ProofNode.to_dict()` for JSON export (consumed by Stage 3 and Stage 5)
- Write ≥4 unit tests in `tests/unit/test_tracer.py`

**Dependencies:** MINILOG-009

**Expected result:**
A tracer that produces human-readable proof trees showing step-by-step derivation of query solutions.

**Acceptance criteria:**
- [ ] 4+ unit tests covering: proof node for a fact, proof node for a rule application, nested proof tree, `to_dict` round-trip
- [ ] `format_tree()` on a proof for a 3-level recursive derivation produces output with the expected indentation and box-drawing characters

---

### MINILOG-012 — Evolution engine

**Description:**
Implement the production-rule engine that mutates the knowledge base over generations, simulating evolution of logical systems.

**What needs to be done:**
- Implement `ProductionRule` dataclass in `minilog/evolution.py`
- Implement `run_generations(kb, rules, n)` that runs `n` generations
- Per generation: for each production rule, find all substitutions satisfying the condition, then apply `add` and `remove` lists under each substitution
- Return a history list of dicts per generation recording added/removed facts
- Write ≥4 unit tests in `tests/unit/test_evolution.py`

**Dependencies:** MINILOG-010

**Expected result:**
An evolution engine that applies production rules to mutate the KB across generations, with a full audit trail.

**Acceptance criteria:**
- [ ] 4+ unit tests covering: add-only rule, remove-only rule, mixed rule, termination after N generations
- [ ] Running a mutation rule 3 times on a seed KB produces the expected cumulative state

---

## Phase 6 — Frontend

### MINILOG-013 — CLI and REPL

**Description:**
Implement the command-line interface and interactive shell that tie all components together into a usable tool.

**What needs to be done:**
- Implement top-level CLI in `minilog/cli.py` using `argparse`: `run`, `repl`, `check`, `version`
- Implement interactive REPL in `minilog/repl.py` with colon-prefixed commands:
  - `:help` — list commands
  - `:quit` | `:q` — exit
  - `:load <file>` — load a `.ml` file into the current KB
  - `:stats` — show KB statistics
  - `:list <functor>/N` — list all facts and rules for a predicate
  - `:evolve <N>` — run N generations of production rules
  - `:saturate` — run forward chaining to fixpoint
  - `:trace on|off` — toggle automatic tracing
  - `:clear` — wipe the KB
- REPL must maintain a persistent `KnowledgeBase` across commands
- Parse each non-`:` line as either a fact, rule, or query
- Pretty-print query results and proof trees
- Handle errors gracefully (catch `MinilogError` subclasses, print, continue)
- Support command history via `readline` when available

**Dependencies:** MINILOG-009, MINILOG-011

**Expected result:**
A fully functional CLI and REPL that loads files, executes queries, displays proof trees, and handles all interactive commands.

**Acceptance criteria:**
- [ ] `minilog run examples/family.ml` produces the expected output
- [ ] `minilog check examples/family.ml` exits 0 on valid input, non-zero on syntax errors
- [ ] `minilog repl` starts, accepts queries, handles `:stats`, `:list`, `:clear`, `:quit`
- [ ] Error messages are English and include line/column when applicable

---

## Phase 7 — Examples

### MINILOG-014 — Examples: family, directions, dwh_dependencies

**Description:**
Author the first three teaching examples and their integration tests, establishing the regression testing pattern.

**What needs to be done:**
- Author `examples/family.ml` — ~10 facts (biblical patriarchs), 4 rules (`тато`, `мама`, `предок` base + recursive), queries for `?- тато(?x, ісак)`, `?- предок(авраам, йосип)`, `?- предок(авраам, ?x)`
- Author `examples/directions.ml` — ~15 facts (Ukrainian city geography), 3 rules (`поруч`, `північніше_транзитивно`), queries about symmetric and transitive relations
- Author `examples/dwh_dependencies.ml` — ~25 facts (tables, procedures, `читає`/`модифікує`/`викликає` relations), ~10 rules, queries for `?- впливає_на(stg_customers, ?x)`, `?- має_цикл(?x)`, `?- конфлікт_запису(?t, ?p1, ?p2)`
- Produce matching `.expected.txt` files by running `minilog run` and reviewing output for correctness
- Write integration tests in `tests/integration/` that assert `minilog run <file>` reproduces expected output byte for byte

**Dependencies:** MINILOG-013

**Expected result:**
Three working examples with verified expected output and passing integration tests.

**Acceptance criteria:**
- [ ] All three examples parse without errors
- [ ] `minilog run examples/family.ml` output matches `examples/family.expected.txt`
- [ ] Same for `directions.ml` and `dwh_dependencies.ml`
- [ ] Integration tests pass
- [ ] `dwh_dependencies.ml` actually detects the seeded cycle and write conflict

---

### MINILOG-015 — Examples: biology, recipes, mythology, causality, terra_tacita

**Description:**
Author the five mid-complexity examples that exercise deeper features: negation, proof trees, multi-layer relations.

**What needs to be done:**
- Author `examples/biology.ml` — ~30 facts (taxonomy + phylogeny), ~8 rules, queries for `?- літає(?x)`, `?- успадковує(дуб, ?p)`, `?- слід успадковує(дуб, хлорофіл)`
- Author `examples/recipes.ml` — ~20 facts (dishes, ingredients, categories), ~5 rules, queries for `?- підходить_вегетаріанцю(?x)`
- Author `examples/mythology.ml` — ~15 facts (Slavic gods, domains, worship), ~4 rules, queries for `?- конфлікт_вірувань(?x, ?y)`
- Author `examples/causality.ml` — ~15 facts (weather/transport causes), ~3 rules, queries for `?- призводить_до(дощ, ?x)`, `?- спільна_причина(мокра_дорога, ?x, ?c)`
- Author `examples/terra_tacita.ml` — ~20 facts with placeholder names, rules for `знає_мову`, `може_говорити_прямо`, `може_говорити_через_артефакт`, `може_спілкуватися`, `може_спілкуватися_через`; **must begin with a prominent multi-line `%` comment disclaimer** that this is a teaching example, NOT the real trilogy canon (the real canon lives in Stage 5)
- Produce matching `.expected.txt` files
- Write integration tests in `tests/integration/`

**Dependencies:** MINILOG-014

**Expected result:**
Five working examples demonstrating negation, proof trees, and complex multi-layer relations.

**Acceptance criteria:**
- [ ] All five examples parse and execute without errors
- [ ] `biology.ml` supports both `?- літає(?x)` and `?- слід успадковує(дуб, хлорофіл)` with proof tree rendered correctly
- [ ] `terra_tacita.ml` starts with the required disclaimer comment
- [ ] All integration tests pass

---

### MINILOG-016 — Evolution example: biology_evolution

**Description:**
Author the evolution example that demonstrates production rules mutating the knowledge base across generations while preserving the validity of existing inference rules.

**What needs to be done:**
- Author `examples/biology_evolution.ml` building on `biology.ml` with ~5 production rules (mutation, speciation, extinction)
- The example exercises the `:evolve N` REPL command
- Produce matching `.expected.txt`
- Write integration test in `tests/integration/test_biology_evolution.py` verifying that after 10 generations, original taxonomy rules still apply to newly evolved species

**Dependencies:** MINILOG-012, MINILOG-015

**Expected result:**
A working evolution example proving that formal-system rules are independent of the specific entities in the knowledge base.

**Acceptance criteria:**
- [ ] `minilog repl examples/biology_evolution.ml` followed by `:evolve 10` runs without errors
- [ ] After evolution, at least one new species exists that was not in the initial KB
- [ ] Querying `?- успадковує(<new_species>, крила)` still produces a valid proof tree using the unchanged base rules
- [ ] Integration test passes

---

## Phase 8 — Documentation

### MINILOG-017 — Documentation and polish

**Description:**
Write the Ukrainian language reference and expand the English README to complete the project documentation.

**What needs to be done:**
- Write `docs/language-reference.md` in **Ukrainian**, documenting:
  - Full syntax with examples
  - The nine built-in examples and what each demonstrates
  - REPL commands
  - CLI commands
  - Error-message conventions
  - Deliberate omissions (no cut, no disjunction, etc.)
- Expand `README.md` (English) with:
  - Installation instructions
  - Quickstart example
  - Link to the Ukrainian language reference
  - Project roadmap pointing at Stages 2–5

**Dependencies:** MINILOG-013, MINILOG-014, MINILOG-015, MINILOG-016

**Expected result:**
Complete project documentation: a Ukrainian language reference for users and an English README for developers.

**Acceptance criteria:**
- [ ] `docs/language-reference.md` covers every language feature from spec section 4
- [ ] `README.md` quickstart runs successfully as documented
- [ ] Both documents render cleanly on GitHub

---

## Phase 9 — REPL Diagnostics

**Rationale:**
In Phase 1 the REPL exposes `:stats` (aggregated counts only) and `:list <functor>/N` (single-predicate view). There is no way to see the full knowledge base at a glance or to discover which predicates are present without reading the source `.ml` file. For a teaching tool this is a real friction point: a learner loads `examples/terra_tacita.ml`, sees `Facts: 24, Rules: 5, Predicates: 9`, and has no way to find out what those 9 predicates actually are without leaving the REPL. Phase 9 closes this gap with three small, orthogonal changes.

### MINILOG-018 — KnowledgeBase.predicates() enumeration method

**Description:**
Add an enumeration method to `KnowledgeBase` that returns a structured list of all predicates in the knowledge base. This is the foundation for both MINILOG-019 and MINILOG-020 and isolates the data-access logic from the REPL presentation layer.

**What needs to be done:**
- Add method `predicates() -> list[tuple[str, int, int, int]]` to `KnowledgeBase` in `minilog/kb.py`
- Each tuple is `(functor, arity, fact_count, rule_count)`
- Include every `(functor, arity)` that has at least one fact or one rule — take the union of `_facts` keys and `_rules` keys
- Return entries sorted alphabetically by functor, then by arity
- A predicate with only rules (zero facts) must still appear with `fact_count=0`
- A predicate with only facts (zero rules) must still appear with `rule_count=0`
- Write ≥3 unit tests in `tests/unit/test_kb.py`: empty KB returns `[]`, mixed facts and rules return correct counts, predicates with same functor but different arities appear as separate entries

**Dependencies:** MINILOG-007

**Expected result:**
A clean API for enumerating all predicates in a knowledge base, usable by the REPL and by any future tool that needs a KB overview (debugger, exporter, static analyzer).

**Acceptance criteria:**
- [ ] `KnowledgeBase().predicates()` returns `[]`
- [ ] After `add_fact(fact("батько", авраам, ісак))` and `add_rule(rule предок/2)`, `predicates()` returns both `("батько", 2, 1, 0)` and `("предок", 2, 0, 1)` in alphabetical order
- [ ] A KB with `батько/1` and `батько/2` returns two separate entries, sorted by arity ascending
- [ ] 3+ unit tests passing
- [ ] No changes to existing `KnowledgeBase` methods (backward compatible)

---

### MINILOG-019 — Enhanced `:stats` with per-predicate breakdown

**Description:**
Extend the `:stats` REPL command so that after the summary line it prints a breakdown of every predicate in the knowledge base, with fact and rule counts. The current `:stats` prints only aggregate numbers and forces users to already know which predicates exist to use `:list`. The enhanced version makes the KB self-describing.

**What needs to be done:**
- Extract the `:stats` handler from the inline branch in `_handle_command` into a new method `_cmd_stats()` in `minilog/repl.py`
- Keep the existing summary line as the first line of output: `Facts: N, Rules: M, Predicates: K`
- After the summary, iterate over `self.kb.predicates()` and print one indented line per predicate in the form `  functor/arity (N facts, M rules)`
- Omit a count component if it is zero: `  предок/2 (2 rules)`, `  батько/2 (12 facts)`, `  вік/2 (4 facts, 1 rule)`
- Use correct English pluralization: `1 fact` / `2 facts`, `1 rule` / `2 rules`
- If the KB is empty, print only the summary line (no breakdown)
- Update `HELP_TEXT` to describe the new behavior: `:stats — show KB statistics with a breakdown by predicate`
- Update `docs/language-reference.md` REPL commands table with the new description
- Write ≥2 integration tests in `tests/integration/` that feed a known KB to the REPL and assert the expected output format

**Dependencies:** MINILOG-018, MINILOG-013

**Expected result:**
`:stats` becomes the primary command for "what is in this KB right now" — summary plus per-predicate inventory, usable without knowing predicate names in advance.

**Acceptance criteria:**
- [ ] Running `:stats` on an empty KB prints `Facts: 0, Rules: 0, Predicates: 0` and nothing else
- [ ] Running `:stats` on `examples/terra_tacita.ml` prints the summary line followed by 9 indented predicate lines (one per predicate) sorted alphabetically
- [ ] Pluralization is correct for both counts of 1 and counts greater than 1
- [ ] Help text reflects the new behavior
- [ ] Language reference updated
- [ ] 2+ integration tests passing

---

### MINILOG-020 — New `:kb` command for full knowledge base dump

**Description:**
Add a new REPL command `:kb` that prints the entire knowledge base grouped by predicate: each predicate introduced by a comment header, followed by all its facts and rules in source-like syntax. This is the diagnostic command for "show me everything" — equivalent to running `:list` on every predicate at once, but without the user having to know the predicate names.

**What needs to be done:**
- Add `:kb` to the command dispatcher in `_handle_command` in `minilog/repl.py`
- Implement `_cmd_kb()` method that:
  - Calls `self.kb.predicates()` to get the predicate inventory
  - If empty, prints `Knowledge base is empty.` and returns
  - Otherwise, for each `(functor, arity, fact_count, rule_count)`:
    - Prints a comment header line: `% functor/arity`
    - Prints each fact indented with two spaces, followed by a period
    - Prints each rule indented with two spaces, in the form `  head :- body1, body2, ...` followed by a period
    - Prints a blank line between predicates for readability
- Output should be valid minilog syntax (ideally, copy-pasting the output back into a file and loading it should reconstruct the same KB, though this is a nice-to-have and not a strict requirement for Phase 9 since the current formatter may not perfectly round-trip Ukrainian operators)
- Add `:kb` to `HELP_TEXT`: `:kb — dump the entire knowledge base (facts and rules)`
- Update `docs/language-reference.md` REPL commands table with the new command
- Write ≥3 integration tests in `tests/integration/`: empty KB case, small KB with one predicate and one rule, loaded `examples/terra_tacita.ml` showing all 9 predicates

**Dependencies:** MINILOG-018, MINILOG-013

**Expected result:**
A one-command way to inspect the full state of a loaded or interactively-built knowledge base, eliminating the need to read the source `.ml` file or to issue `:list` many times.

**Acceptance criteria:**
- [ ] `:kb` on empty KB prints `Knowledge base is empty.`
- [ ] `:kb` after loading `examples/terra_tacita.ml` prints all 24 facts and all 5 rules, grouped by predicate, with `% functor/arity` headers
- [ ] Predicates appear in the same alphabetical order as in `:stats`
- [ ] Blank line separates predicate groups
- [ ] Help text includes `:kb`
- [ ] Language reference updated
- [ ] 3+ integration tests passing

---

## Phase 9 — Arithmetic Expressions

**Rationale:**
In Phase 1 the evaluator only understands `Num` terms and variables that walk to `Num` terms. Comparison goals like `?n ≥ 18` work because `?n` resolves to a plain number, but any compound expression fails. The lexer does not even produce tokens for `+`, `-`, `*`, `/`, so attempts to write `?a * ?a + ?b * ?b = ?c * ?c` raise `LexError` on the first `*`. This blocks all but the most trivial numeric reasoning: you cannot verify the Pythagorean theorem, compute a triangle side length, derive a midpoint, or express any formula from high-school geometry.

This block of four issues extends minilog with enough arithmetic to handle real numeric reasoning while staying within the teaching-prototype spirit: only expressions inside comparison goals (no `is/2`-style assignment), only four basic operators plus three built-in functions (`sqrt`, `abs`, `pow`), no user-defined infix operators, no arithmetic in rule heads. The changes are a strict, well-scoped extension of the existing infrastructure: lexer gains four tokens, parser gains an expression level above comparisons, evaluator gains recursive traversal of compound terms with a small builtin dispatch table.

**Note on deliberate omissions:** the `language-reference.md` section "Свідомі обмеження" currently states that infix operators other than comparisons are not supported. This is still true for user-defined operators after Phase 9. Arithmetic operators are a built-in exception, not a user-extensible mechanism. MINILOG-024 updates the reference to make this distinction explicit.

### MINILOG-021 — Lexer support for arithmetic operators and negative numbers

**Description:**
Extend the lexer to recognize the four arithmetic operators as tokens and to correctly tokenize negative numeric literals. This is the prerequisite for any expression parsing and is a pure, self-contained change to `lexer.py` with no impact on other modules.

**What needs to be done:**
- Add four new token types to `TokenType` in `minilog/lexer.py`:
  - `OP_PLUS` for `+`
  - `OP_MINUS` for `-`
  - `OP_STAR` for `*`
  - `OP_SLASH` for `/`
- Extend `tokenize` to emit these tokens when the corresponding characters are encountered
- Handle unary minus on numeric literals: if `-` is immediately followed by a digit AND the previous token is one of `LPAREN`, `COMMA`, `OP_GE`, `OP_LE`, `OP_GT`, `OP_LT`, `OP_EQ`, `OP_NE`, `OP_PLUS`, `OP_MINUS`, `OP_STAR`, `OP_SLASH`, `KW_IF`, `KW_AND`, `NEWLINE`, `INDENT`, or the start of input, emit a single `INT`/`FLOAT` token with a negative value. Otherwise `-` is tokenized as `OP_MINUS`
- The intuition: after something that can be followed by an expression, a `-` followed by a digit is part of the number. After an identifier or a closing paren, `-` is the subtraction operator
- Write ≥6 unit tests in `tests/unit/test_lexer.py`:
  - Each of `+`, `-`, `*`, `/` tokenizes as its respective `OP_*` token
  - `-5` at the start of a line tokenizes as a single `INT` with value `-5`
  - `?a - 5` tokenizes as `VAR`, `OP_MINUS`, `INT(5)` (subtraction, not negative number)
  - `(-5)` tokenizes as `LPAREN`, `INT(-5)`, `RPAREN`
  - `?a * -5` tokenizes as `VAR`, `OP_STAR`, `INT(-5)`
  - `3.14 / 2` tokenizes as `FLOAT`, `OP_SLASH`, `INT`

**Dependencies:** MINILOG-004

**Expected result:**
A lexer that produces arithmetic operator tokens and correctly distinguishes unary minus on numeric literals from binary subtraction, leaving the parser free to consume a clean token stream.

**Acceptance criteria:**
- [ ] All four arithmetic operator tokens defined and emitted
- [ ] Negative literals handled correctly for `INT` and `FLOAT`
- [ ] Existing lexer tests still pass (no regression)
- [ ] 6+ new unit tests passing
- [ ] No changes to `parser.py`, `evaluator.py`, or any other module

---

### MINILOG-022 — Parser support for arithmetic expressions in comparison goals

**Description:**
Extend the parser to recognize arithmetic expressions wherever a numeric term is expected inside a comparison goal. The parser must handle operator precedence (`*` and `/` bind tighter than `+` and `-`), left-associativity, parenthesized sub-expressions, and unary minus on non-literal terms. Arithmetic is accepted **only** inside comparison goals, not in rule heads or in regular compound term arguments — this matches Prolog's convention where `is/2` is the traditional arithmetic entry point.

**What needs to be done:**
- Add a new non-terminal `expression` to the parser in `minilog/parser.py`
- Grammar (informal):
  ```
  comparison    = expression comparison_op expression
  expression    = term_add { ("+" | "-") term_add }
  term_add      = factor { ("*" | "/") factor }
  factor        = "-" factor | primary
  primary       = NUMBER | VAR | compound_call | "(" expression ")"
  compound_call = IDENT "(" expression { "," expression } ")"
  ```
- Compound calls in expressions represent built-in function invocations (`sqrt(?x)`, `pow(?a, 2)`, `abs(?x - ?y)`); they are parsed as `Compound` terms and left to the evaluator to interpret. A compound call with a functor that is not a recognized built-in will fail at evaluation time, not at parse time
- Left-associativity: `?a - ?b - ?c` parses as `(?a - ?b) - ?c`, not `?a - (?b - ?c)`
- Precedence: `?a + ?b * ?c` parses as `?a + (?b * ?c)`
- Parentheses override precedence: `(?a + ?b) * ?c` parses as expected
- Expression AST representation: reuse the existing `Compound` term class with functors `"+"`, `"-"`, `"*"`, `"/"`, all of arity 2, plus `Compound("-", (expr,))` of arity 1 for unary minus
- Arithmetic is **only** valid inside a comparison goal. In rule heads and regular compound arguments, encountering `+`, `-`, `*`, or `/` is a parse error. This preserves the existing simple AST for facts and rule heads
- Update the EBNF section of `docs/language-reference.md` (kept consistent with MINILOG-024)
- Write ≥8 unit tests in `tests/unit/test_parser.py`:
  - Simple addition: `?a + ?b = 10`
  - Precedence: `?a + ?b * ?c = ?d` produces the correct AST
  - Left-associativity: `?a - ?b - ?c` parses as `(?a - ?b) - ?c`
  - Parentheses: `(?a + ?b) * ?c = ?d`
  - Nested: `?a * ?a + ?b * ?b = ?c * ?c`
  - Unary minus on variable: `-?a < 0`
  - Built-in function call: `sqrt(?x * ?x + ?y * ?y) = ?d`
  - Arithmetic in rule head is rejected: `правило подвійний(?x, ?x + ?x).` raises `ParseError`

**Dependencies:** MINILOG-021, MINILOG-005

**Expected result:**
A parser that accepts arithmetic expressions in comparison goals with standard precedence and associativity, represented as nested `Compound` terms that the evaluator can walk recursively. Outside of comparison goals the grammar is unchanged.

**Acceptance criteria:**
- [ ] All eight test cases pass
- [ ] Existing parser tests still pass
- [ ] Arithmetic in rule heads produces a clear `ParseError` with line/column info
- [ ] EBNF in `language-reference.md` updated (as part of MINILOG-024 acceptance, but the parser change must not break the existing grammar)

---

### MINILOG-023 — Evaluator support for compound arithmetic terms and built-in functions

**Description:**
Extend the evaluator to recursively compute arithmetic expressions represented as compound terms and to dispatch three built-in mathematical functions (`sqrt`, `abs`, `pow`). This is the runtime counterpart of MINILOG-022 and is what actually makes `?a * ?a + ?b * ?b = ?c * ?c` compute a truth value.

**What needs to be done:**
- Rewrite `evaluate(term, subst)` in `minilog/evaluator.py` so that it walks compound terms recursively:
  - If resolved term is `Num`, return it (current behavior)
  - If resolved term is `Var`, raise `EvaluatorError("unbound variable ...")` (current behavior)
  - If resolved term is `Compound` with functor in `{"+", "-", "*", "/"}` and arity 2, recursively evaluate both arguments and apply the operation. Division by zero raises `EvaluatorError("division by zero")`
  - If resolved term is `Compound` with functor `"-"` and arity 1, recursively evaluate the argument and negate it (unary minus)
  - If resolved term is `Compound` with functor in `{"sqrt", "abs", "pow"}`, dispatch to the corresponding built-in:
    - `sqrt/1`: argument must be non-negative, otherwise raise `EvaluatorError("sqrt of negative number")`
    - `abs/1`: return absolute value
    - `pow/2`: return `base ** exponent`, with special handling for integer bases and integer exponents to preserve int type (e.g., `pow(2, 3) = 8`, not `8.0`); float result otherwise
  - If resolved term is `Compound` with any other functor, raise `EvaluatorError(f"unknown arithmetic function {functor}/{arity}")`
  - If resolved term is any other type (`Atom`, `Str`), raise the existing `EvaluatorError` for non-numeric
- Integer vs float semantics: `+`, `-`, `*` preserve integer type if both operands are integers. `/` always returns float (like Python 3 `/`). Explicit integer division can be added later as `//` if needed — not in this issue
- `check_comparison` is unchanged — it already calls `evaluate` on both sides, so the recursive evaluator transparently handles expressions
- Write ≥10 unit tests in `tests/unit/test_evaluator.py`:
  - Plain number: `evaluate(Num(5)) = 5` (regression)
  - Variable walk to number: regression
  - Addition: `evaluate(Compound("+", (Num(3), Num(4)))) = 7`
  - Nested: `evaluate(Compound("+", (Num(3), Compound("*", (Num(4), Num(5)))))) = 23`
  - Division preserves float: `evaluate(Compound("/", (Num(10), Num(4)))) = 2.5`
  - Division by zero raises `EvaluatorError`
  - Unary minus: `evaluate(Compound("-", (Num(5),))) = -5`
  - `sqrt(16) = 4.0`
  - `sqrt(-1)` raises `EvaluatorError`
  - `pow(2, 10) = 1024` (integer)
  - `abs(-7) = 7`
  - Unknown function raises `EvaluatorError` with functor/arity in message
- Also write ≥3 integration tests in `tests/integration/` that exercise comparison goals with expressions from actual minilog source:
  - Pythagorean check: `правило прямокутний(?a, ?b, ?c) якщо ?a * ?a + ?b * ?b = ?c * ?c.`
  - Distance check: `правило близько(?x1, ?y1, ?x2, ?y2) якщо sqrt((?x2 - ?x1) * (?x2 - ?x1) + (?y2 - ?y1) * (?y2 - ?y1)) < 5.`
  - Triangle inequality: `правило валідний_трикутник(?a, ?b, ?c) якщо ?a + ?b > ?c і ?b + ?c > ?a і ?a + ?c > ?b.`

**Dependencies:** MINILOG-022, MINILOG-008

**Expected result:**
A fully functional numeric evaluator that handles arbitrary nested arithmetic expressions and three essential math functions, enabling real numeric reasoning in minilog programs. The Pythagorean theorem, triangle inequality, and Euclidean distance all become expressible in one line.

**Acceptance criteria:**
- [ ] All ten unit tests and three integration tests pass
- [ ] Existing evaluator tests still pass
- [ ] Error messages are informative and include the offending functor when applicable
- [ ] Integer/float type preservation matches the specification above
- [ ] No changes to `unify.py`, `engine.py`, or the term model

---

### MINILOG-024 — Arithmetic documentation, examples, and language reference update

**Description:**
With arithmetic now functional at the lexer, parser, and evaluator levels, the user-facing documentation must be updated and a small demonstration example must be added to the `examples/` directory. This issue is the finishing touch that makes the arithmetic feature discoverable and teachable.

**What needs to be done:**
- Update `docs/language-reference.md`:
  - Add a new section "Арифметика" between "Порівняння" and "Коментарі" sections
  - Document the four arithmetic operators with precedence and associativity
  - Document the three built-in functions (`sqrt`, `abs`, `pow`) with signatures and semantics
  - Show example comparison goals using expressions: Pythagorean theorem, Euclidean distance, triangle inequality
  - Update the EBNF grammar section to include the expression non-terminal
  - Update the "Свідомі обмеження" section: the statement about infix operators must be refined. Currently it says infix operators other than comparisons are not supported. Rewrite as: arithmetic operators (`+`, `-`, `*`, `/`) are built-in inside comparison goals. User-defined infix operators are still not supported. This preserves the Phase 1 design philosophy while accurately reflecting the new capability
- Create `examples/arithmetic_demo.ml`:
  - ~10 facts representing points with coordinates: `точка(a, 0, 0).`, `точка(b, 3, 0).`, `точка(c, 0, 4).`, etc.
  - ~5 rules using arithmetic: Euclidean distance check, Pythagorean triple detection, quadrant classification (via sign comparison), midpoint validation, triangle inequality
  - ~4 queries demonstrating each arithmetic feature: basic addition, multiplication, sqrt, pow
  - Include a traced query (`?- слід ...`) to show how the proof tree renders arithmetic comparison goals
  - Include a prominent multi-line `%` header comment explaining what this example demonstrates and linking to the arithmetic section of the language reference
- Produce matching `examples/arithmetic_demo.expected.txt`
- Write integration test `tests/integration/test_arithmetic_demo.py` that asserts `minilog run examples/arithmetic_demo.ml` reproduces the expected output byte for byte

**Dependencies:** MINILOG-023

**Expected result:**
Arithmetic is fully documented, one new example file demonstrates real-world usage, and the language reference accurately describes what the user can now do. A reader of `language-reference.md` should be able to write a Pythagorean theorem check without any other resources.

**Acceptance criteria:**
- [ ] New section "Арифметика" in `language-reference.md` with operators, functions, precedence, and examples
- [ ] EBNF grammar updated to include expression production
- [ ] "Свідомі обмеження" section updated to distinguish built-in vs user-defined infix operators
- [ ] `examples/arithmetic_demo.ml` parses and runs without errors
- [ ] `examples/arithmetic_demo.expected.txt` matches actual output
- [ ] Integration test passes
- [ ] Traced query in the example renders proof tree correctly with arithmetic goals

---

**Phase 9 scope notes (updated):**

Phase 9 now contains two independent blocks: **REPL Diagnostics** (MINILOG-018, 019, 020) and **Arithmetic Expressions** (MINILOG-021, 022, 023, 024). The two blocks do not interact with each other and can be developed in parallel or in any order.

**REPL Diagnostics block:**
- All three tasks are Size S (≤0.5 day each). Total effort: ~1 day.
- MINILOG-018 must be merged before MINILOG-019 and MINILOG-020 start, since both call `KnowledgeBase.predicates()`.
- MINILOG-019 and MINILOG-020 are independent of each other and can be done in parallel.
- Affects only `kb.py`, `repl.py`, and documentation.
- The existing `:list <functor>/N` command remains unchanged.

**Arithmetic Expressions block:**
- Four tasks totaling ~3 days of effort (S + M + M + S).
- Strictly sequential: MINILOG-021 → MINILOG-022 → MINILOG-023 → MINILOG-024. Each depends on the previous one.
- Affects `lexer.py`, `parser.py`, `evaluator.py`, `docs/language-reference.md`, and adds one new file `examples/arithmetic_demo.ml` plus its expected output and integration test.
- No changes to `terms.py` (reuses existing `Compound` for expression AST), `unify.py`, `engine.py`, `kb.py`, `tracer.py`, `forward.py`, or `evolution.py`.
- No new external dependencies.
- After Phase 9 arithmetic is merged, the geometry example (planned separately) will become feasible, since it requires `sqrt`, `pow`, and nested arithmetic expressions for the Pythagorean theorem and Euclidean distance.

**Overall Phase 9 effort:** ~4 days if done sequentially, ~3 days if REPL Diagnostics and Arithmetic Expressions blocks run in parallel.

---

## Phase 10 — Geometry

**Rationale:**
With Phase 9 arithmetic (MINILOG-021..024) in place, minilog gains the numerical expressiveness needed to model real geometry: Euclidean distance via `sqrt` and `pow`, the Pythagorean theorem as a one-line comparison goal, triangle inequality as a conjunction of three additions. This unlocks a class of examples that was impossible in the original Phase 1 set: geometric reasoning with computed quantities.

Phase 10 adds a single large example — triangle classification and elementary theorems — as a complete package: the `.ml` source, expected output and integration test, a companion explanation document, and updates to the language reference and README. It is the fourth major thematic example after `family` (kinship), `biology` (taxonomy), and `dwh_dependencies` (enterprise data), filling the gap for numerical/geometric reasoning.

**Design choices** (locked before implementation):

1. **Coordinates are given as facts, not computed.** A point is stored as `точка(a, 0, 0).` — the user places points, minilog classifies triangles. This keeps the example focused on logical classification, not numerical construction.
2. **Side lengths are computed via `sqrt(pow(dx, 2) + pow(dy, 2))`.** This exercises the new arithmetic directly and demonstrates that formulas from high-school geometry become one-line rules.
3. **Angles are given as facts per triangle.** Minilog has no trigonometry built in. Classification by angle (acute/right/obtuse) uses angle facts; classification by side length (equilateral/isosceles/scalene) uses computed distances.
4. **Classification is hierarchical.** Equilateral implies isosceles. Proof trees for "equilateral" show this composition explicitly, mirroring the pattern from `biology.ml`.
5. **Theorems proved by minilog:** triangle inequality, Pythagorean relation for a specific right triangle, hierarchical classification, SSS congruence.
6. **No Euclidean constructions.** No circles, no intersection points, no compass-and-straightedge. Phase 10 stays within "given points, classify and verify."

### MINILOG-025 — Geometry example: triangle classification and theorems (.ml file)

**Description:**
Author `examples/geometry_triangles.ml` — the core source file for the Phase 10 geometry example. Demonstrates arithmetic-powered reasoning about triangles: computing side lengths from point coordinates via `sqrt` and `pow`, classifying by sides and angles, verifying the triangle inequality, and checking the Pythagorean relation.

**What needs to be done:**

- Create `examples/geometry_triangles.ml` with header comment, ~8 point facts (including `точка(a, 0, 0).`, `точка(b, 4, 0).`, `точка(c, 0, 3).` to form a 3-4-5 right triangle), ~6 triangle facts (including one collinear degenerate case), ~15 angle facts
- Distance computed inline via `sqrt(pow(?x2 - ?x1, 2) + pow(?y2 - ?y1, 2))` inside comparison goals. Rules compare two distance expressions directly without binding to an intermediate variable, because backward chaining requires both sides of `=` to be computable at evaluation time
- Classification rules: `рівнобедрений/1`, `рівносторонній/1` (hierarchical — implies `рівнобедрений` via a separate rule), `різносторонній/1`, `прямокутний/1`, `гострокутний/1`, `тупокутний/1`, `валідний_трикутник/1`, `піфагоровий/1`, `конгруентні_sss/2`
- ~8 queries exercising classification, theorems, and two traced queries (Pythagorean check, isosceles)
- Do NOT create `.expected.txt` or tests here — those are MINILOG-026

**Dependencies:** MINILOG-023

**Acceptance criteria:**
- [ ] File parses and runs without errors
- [ ] `валідний_трикутник(t5)` false for collinear case
- [ ] `піфагоровий(t1)` true for 3-4-5 triangle
- [ ] Proof trees visibly include arithmetic goals
- [ ] 60-100 lines total

### MINILOG-026 — Geometry example: expected output and integration test

**Description:**
Produce `examples/geometry_triangles.expected.txt` and write an integration test that verifies `minilog run examples/geometry_triangles.ml` reproduces the expected output byte for byte. Follows the same pattern as `test_family.py`, `test_biology.py`, etc.

**What needs to be done:**

- Run `minilog run examples/geometry_triangles.ml` on a stable post-MINILOG-025 build, capture stdout, review for correctness (each query returns the expected number of solutions, arithmetic values are correct — e.g., `sqrt(25) = 5.0`, the 3-4-5 triangle has sides of length 3, 4, 5)
- Save as `examples/geometry_triangles.expected.txt`
- Write `tests/integration/test_geometry_triangles.py` following existing integration test patterns in that directory
- Test loads the example via CLI, compares output to expected file byte-for-byte, fails with a clear diff on mismatch

**Dependencies:** MINILOG-025

**Acceptance criteria:**
- [ ] `examples/geometry_triangles.expected.txt` exists and matches current output
- [ ] `pytest tests/integration/test_geometry_triangles.py` passes
- [ ] Expected output includes at least one traced query with visible arithmetic goal in the proof tree
- [ ] File is UTF-8 and Ukrainian text displays correctly
- [ ] Test structure matches other integration tests in the directory

### MINILOG-027 — Geometry example: theoretical companion document

**Description:**
Write `docs/geometry-triangles-explained.md` — a standalone Ukrainian-language document explaining the theoretical and practical foundations of the geometry example. Pedagogical counterpart to the `.ml` file, similar in style to `prolog-engine-explained.md`. Bridges from "what is in the file" to "why it works and what it teaches."

**What needs to be done:**

Create `docs/geometry-triangles-explained.md` with nine sections (Ukrainian main text, English technical terms, no emoji, style matching `prolog-state-2025.md` and `prolog-engine-explained.md`):

1. **Introduction** — what the document covers, who it is for, relation to `examples/geometry_triangles.ml` and Phase 9 arithmetic
2. **Geometry as a formal axiomatic system** — Euclid's approach (axioms + common notions + definitions → theorems), how this maps to Horn clauses (axioms become facts and rules, theorems become queries), short note on Hilbert's formalization
3. **What the example models** — points as `(name, x, y)` facts, triangles as `(name, p1, p2, p3)` facts, angles as `(triangle, vertex, degrees)` facts. Why coordinates are given not computed. Why this is still legitimate formal reasoning
4. **Computing side lengths** — distance formula as a one-line rule using `sqrt(pow(x2-x1, 2) + pow(y2-y1, 2))`. Walk through type preservation. Why `=` on two `sqrt` expressions works (both sides are computed, comparison is numerical equality after walking both expressions to ground floats)
5. **Classification by sides** — isosceles, equilateral, scalene. Hierarchical relationship: equilateral ⊂ isosceles. Proof tree for equilateral triangle shows this composition
6. **Classification by angles** — right, acute, obtuse. Why angles are given as facts not computed. Future extension: if `sin`/`cos`/`atan2` were added, angles could be computed from coordinates
7. **Theorems verified** — triangle inequality, Pythagorean theorem, SSS congruence. Each in minilog syntax with discussion of proof tree structure
8. **Strengths and limitations** — Strengths: declarative rules map directly to geometric properties, proof trees are real geometric arguments. Limitations: no circles, no intersection points, no numerical solver, no trigonometry. What would require Phase 11+
9. **Connection to broader context** — brief note that this example is a concrete realization of "formal systems as reasoners over computed quantities." Geometry was one of the first formal systems (Euclid ~300 BCE), and mechanizing elementary triangle reasoning in ~80 lines of minilog demonstrates the tradition from Euclid through Hilbert to Kowalski to modern logic programming. Further reading and extensions

**Formatting:** ~8-12 pages (400-600 markdown lines), Ukrainian text with English technical terms, no emoji, all code snippets must match `examples/geometry_triangles.ml` exactly, cross-links to `language-reference.md` (Arithmetic section) and `prolog-engine-explained.md`.

**Dependencies:** MINILOG-025

**Acceptance criteria:**
- [ ] Document exists at `docs/geometry-triangles-explained.md`
- [ ] Length 8-12 pages
- [ ] All code snippets match `examples/geometry_triangles.ml`
- [ ] Cross-links work
- [ ] No emoji
- [ ] Renders cleanly on GitHub preview

### MINILOG-028 — Geometry example: language reference and README integration

**Description:**
Integrate the new geometry example into user-facing documentation surfaces: add it to the examples list in `docs/language-reference.md`, update `README.md` to mention it, make sure readers can discover it naturally.

**What needs to be done:**

- Update `docs/language-reference.md`:
  - Add entry for `geometry_triangles.ml` in the "Приклади" section, describing what it demonstrates (triangle classification, distance computation, Pythagorean theorem, hierarchical classification)
  - Link to `docs/geometry-triangles-explained.md` for theoretical background
  - Note that this example requires Phase 9 arithmetic features
- Update `README.md`:
  - Add mention of `geometry_triangles.ml` in the examples list or quickstart section
  - One-sentence description: "Triangle classification and elementary theorems, demonstrating arithmetic expressions (requires Phase 9)"
  - Link to the companion document
- If README has a roadmap, update Phase 10 status from planned to complete
- Verify all cross-links work

**Dependencies:** MINILOG-025, MINILOG-027

**Acceptance criteria:**
- [ ] `language-reference.md` examples section includes new entry with link
- [ ] `README.md` mentions the geometry example
- [ ] All cross-links verified in local markdown preview
- [ ] No broken links
- [ ] If README has roadmap, Phase 10 status updated

---

**Phase 10 scope notes:**

Phase 10 is a **single cohesive package** — one example delivered with full supporting material. Unlike Phase 9 (two independent blocks), Phase 10 is strictly sequential because every issue depends on the previous:

- MINILOG-025 creates the source file
- MINILOG-026 needs the source file to run and produce expected output
- MINILOG-027 needs the source file to quote from accurately
- MINILOG-028 needs both source and companion doc to link to

**Total effort:** ~3-4 days (M + S + M + S).

**Hard prerequisite:** Phase 9 Arithmetic Expressions block (MINILOG-021..024) must be fully merged and working before Phase 10 starts. Without `sqrt`, `pow`, and arithmetic comparison goals, the example cannot be authored.

**Files created by Phase 10:**
- `examples/geometry_triangles.ml` (~80 lines)
- `examples/geometry_triangles.expected.txt` (generated)
- `tests/integration/test_geometry_triangles.py` (~30 lines)
- `docs/geometry-triangles-explained.md` (~500 lines)

**Files modified by Phase 10:**
- `docs/language-reference.md` (examples list)
- `README.md` (examples list / roadmap)

**Files NOT touched by Phase 10:**
- Any file in `minilog/` — Phase 10 is purely additive content. All engine work was completed in Phase 9.

**After Phase 10 is merged,** minilog has a fourth major thematic example covering the numerical/geometric domain, completing the original teaching set (kinship / taxonomy / enterprise data / geometry) and demonstrating that Phase 9 arithmetic enabled a whole new class of declarative reasoning.