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
