# minilog Phase 15 — Lists and Built-ins Plan

## Issues Summary Table

| # | ID | Title | Size | Phase | Dependencies |
|---|---|---|---|---|---|
| 59 | MINILOG-059 | Term model extension for List type | M | 15.1 — Lists Core | MINILOG-002 |
| 60 | MINILOG-060 | Lexer support for list syntax tokens | S | 15.1 — Lists Core | MINILOG-059, MINILOG-004 |
| 61 | MINILOG-061 | Parser support for list literals and `[H\|T]` | M | 15.1 — Lists Core | MINILOG-060, MINILOG-005 |
| 62 | MINILOG-062 | Unification for list terms | M | 15.1 — Lists Core | MINILOG-059, MINILOG-006 |
| 63 | MINILOG-063 | Tracer formatting for lists | S | 15.1 — Lists Core | MINILOG-062, MINILOG-011 |
| 64 | MINILOG-064 | Lists core documentation and basic examples | S | 15.1 — Lists Core | MINILOG-063 |
| 65 | MINILOG-065 | `member/2` and `append/3` in stdlib | S | 15.2 — List Built-ins | MINILOG-064 |
| 66 | MINILOG-066 | `length/2` and `nth0/3` with arithmetic | M | 15.2 — List Built-ins | MINILOG-065, MINILOG-024 |
| 67 | MINILOG-067 | `last/2`, `reverse/2`, `msort/2` additional predicates | S | 15.2 — List Built-ins | MINILOG-065 |
| 68 | MINILOG-068 | stdlib documentation and loader mechanism | S | 15.2 — List Built-ins | MINILOG-067 |
| 69 | MINILOG-069 | `findall/3` engine implementation | M | 15.3 — Meta-predicates | MINILOG-064, MINILOG-009 |
| 70 | MINILOG-070 | `bagof/3` and `setof/3` | M | 15.3 — Meta-predicates | MINILOG-069 |
| 71 | MINILOG-071 | Meta-predicates documentation | S | 15.3 — Meta-predicates | MINILOG-070 |
| 72 | MINILOG-072 | Type inspection: `var`, `nonvar`, `atom`, `number`, `ground` | S | 15.4 — Small Built-ins | MINILOG-009 |
| 73 | MINILOG-073 | Extended negation for conjunctions | S | 15.4 — Small Built-ins | MINILOG-009 |
| 74 | MINILOG-074 | Generic graph coloring example | M | 15.5 — Advanced Examples | MINILOG-068, MINILOG-069 |
| 75 | MINILOG-075 | Generic hamiltonian path example | M | 15.5 — Advanced Examples | MINILOG-068, MINILOG-069 |
| 76 | MINILOG-076 | Tic-tac-toe example with winning moves | M | 15.5 — Advanced Examples | MINILOG-068, MINILOG-069, MINILOG-072 |
| 77 | MINILOG-077 | N-queens example | M | 15.5 — Advanced Examples | MINILOG-068, MINILOG-069 |
| 78 | MINILOG-078 | Phase 15 advanced examples documentation | S | 15.5 — Advanced Examples | MINILOG-077 |
| 79 | MINILOG-079 | `call/N` and `forall/2` meta-predicates | M | 15.3 — Meta-predicates | MINILOG-069 |
| 80 | MINILOG-080 | Disjunction operator `або` | S | 15.6 — Syntax Extensions | MINILOG-005 |
| 81 | MINILOG-081 | Custom infix operators via `op/3` directive | L | 15.6 — Syntax Extensions | MINILOG-080 |
| 82 | MINILOG-082 | Phase 15.6 syntax extensions documentation | S | 15.6 — Syntax Extensions | MINILOG-081 |
| 83 | MINILOG-083 | String core predicates: length, concat, chars | M | 15.7 — String Manipulation | MINILOG-009 |
| 84 | MINILOG-084 | String transformations: upper, lower, sub_string, split | M | 15.7 — String Manipulation | MINILOG-083, MINILOG-064 |
| 85 | MINILOG-085 | Phase 15.7 string manipulation documentation | S | 15.7 — String Manipulation | MINILOG-084 |
| 86 | MINILOG-086 | Example: disjunction in family relations | S | 15.8 — Feature Examples | MINILOG-080 |
| 87 | MINILOG-087 | Example: natural-syntax ontology with custom operators | M | 15.8 — Feature Examples | MINILOG-081 |
| 88 | MINILOG-088 | Example: polymorphic describe via type inspection | S | 15.8 — Feature Examples | MINILOG-072 |
| 89 | MINILOG-089 | Example: higher-order programming via `call/N` and `forall` | M | 15.8 — Feature Examples | MINILOG-079, MINILOG-064 |
| 90 | MINILOG-090 | Example: text processing with string predicates | M | 15.8 — Feature Examples | MINILOG-084 |
| 91 | MINILOG-091 | Example: integrated library catalog showcase | M | 15.8 — Feature Examples | MINILOG-081, MINILOG-080, MINILOG-069, MINILOG-084 |
| 92 | MINILOG-092 | Phase 15.8 feature examples documentation | S | 15.8 — Feature Examples | MINILOG-091 |

**Size legend:** S = ≤ 0.5 day, M = 0.5–1 day, L = 1–2 days

---

## Locked Architectural Decisions

| Decision | Choice |
|---|---|
| List internal representation | Compound terms with dot functor (`.(H, T)` and `[]` atom), classical Prolog style |
| List surface syntax | `[1, 2, 3]` for literals, `[H\|T]` for head/tail deconstruction, `[]` for empty |
| Nested lists allowed | Yes — lists can contain lists and any other terms |
| Mixed-type lists allowed | Yes — a list can contain atoms, numbers, compound terms, and other lists |
| stdlib location | New file `minilog/stdlib.ml` auto-loaded by REPL and CLI on startup |
| stdlib loader mechanism | Automatic on engine initialization; can be disabled via `--no-stdlib` flag |
| Built-in list predicates as | Pure minilog rules in `stdlib.ml` where possible, fallback to Python built-ins only when rules are infeasible |
| Meta-predicate `findall/3` | Implemented in Python inside `engine.py` as a special form, not as a rule |
| `bagof/3` and `setof/3` | Included in Phase 15.3, not optional — completes the meta-predicate family |
| `var/1` and `nonvar/1` | Python built-ins with explicit documentation warning about non-declarative nature |
| Cut (`!`) | **Explicitly rejected** — breaks declarative semantics, not included in Phase 15 |
| Disjunction operator | Ukrainian keyword `або` added as parser-level sugar over split rules; backend treats disjunction as two branches with backtrack |
| Custom infix operators | Supported via `op/3` directive with fixity types `xfx`, `xfy`, `yfx` for binary operators; enables natural syntax like `сократ є людина` |
| String representation | Separate `Str` type (already exists in minilog); all string operations work on `Str`, not on atoms or char-code lists |
| String operations scope | Core predicates (length, concat, chars) plus transformations (upper, lower, sub_string, split); no regex, no format, no I/O |
| `call/N` arity | Variadic up to call/7 (Goal plus 6 extra args), covers all practical meta-call patterns |
| Meta-predicate family completeness | `findall/3`, `bagof/3`, `setof/3`, `call/N`, `forall/2` — the classical Prolog meta-predicate set |
| Extended negation scope | `не` expanded to accept conjunctions of goals, parser change only |
| Anonymous variables in lists | `_` in list context still works as before — introduces fresh unbound variable |
| Max list length | Practical limit from Python recursion depth, no artificial constraint |
| Arithmetic dependency | `length/2`, `nth0/3`, `nth1/3` require Phase 9 arithmetic (MINILOG-024) |
| Backwards compatibility | All existing `.ml` files continue to work unchanged — lists are purely additive |

---

## Phase 15.1 — Lists Core

**Rationale:**
Lists are the single most important missing feature in minilog Phase 1. Without them, generic algorithms over collections are impossible — rules must have fixed arity, which means a graph coloring rule for 5 vertices needs a different rule from one for 6 vertices, and "process all elements" patterns cannot be expressed naturally. Every non-trivial Prolog example in textbooks uses lists; every classical algorithm (sort, search, map, filter, reduce) assumes them.

Phase 15.1 adds lists as a first-class data type to minilog. The representation follows classical Prolog exactly: a list is either the empty list atom `[]` or a compound term `.(Head, Tail)` where `Tail` is itself a list. Surface syntax supports both `[1, 2, 3]` literals and `[H|T]` deconstruction patterns. Unification works recursively through list structure, which means `[X, Y, Z]` unifies with `[1, 2, 3]` binding `X=1, Y=2, Z=3`, and `[H|T]` unifies with `[1, 2, 3]` binding `H=1, T=[2, 3]`.

This phase touches six minilog modules (`terms.py`, `lexer.py`, `parser.py`, `unify.py`, `tracer.py`, and adds new integration tests) but leaves the engine (`engine.py`) largely untouched — lists are just a new term type that flows through the existing resolution machinery.

After Phase 15.1, the user can write and query rules that take lists as arguments and deconstruct them through pattern matching. Phase 15.2 then builds on this foundation with a standard library of list predicates.

### MINILOG-059 — Term model extension for List type

**Description:**
Extend the term model in `minilog/terms.py` to represent lists as compound terms using classical Prolog dot-functor convention. A list is either the empty list atom `[]` or a compound term with functor `.` and two arguments: head element and tail list. This representation is equivalent to Lisp's cons cells and allows lists to flow through the existing unification and evaluation machinery without special cases in the engine.

**What needs to be done:**
- In `minilog/terms.py`, add a module-level constant `EMPTY_LIST = Atom("[]")` representing the empty list
- Add helper constructors for lists:
  - `make_list(elements: list[Term]) -> Term` — builds `.(e1, .(e2, .(e3, [])))` from `[e1, e2, e3]`
  - `make_cons(head: Term, tail: Term) -> Compound` — builds `.(head, tail)` (a single cons cell)
  - `is_list(term: Term) -> bool` — walks the term and returns True if it is a proper list (terminated with `[]`)
  - `list_elements(term: Term) -> list[Term] | None` — deconstructs a proper list into a Python list; returns None for partial or non-list terms
- Document the representation choice in a docstring at the top of the module
- Write ≥6 unit tests in `tests/unit/test_terms_list.py`:
  - Empty list construction and recognition
  - Single-element list `[a]` roundtrip through make_list/list_elements
  - Multi-element list `[1, 2, 3]` roundtrip
  - Nested list `[[1, 2], [3, 4]]` roundtrip
  - Partial list `[1, 2 | X]` returns None from list_elements when X is unbound
  - Mixed-type list with atoms, numbers, compound terms
- No changes to `Atom`, `Num`, `Var`, `Compound` — the existing `Compound` class already handles dot-functor cons cells because it is generic over functor names

**Dependencies:** MINILOG-002

**Expected result:**
A working list representation at the term level. Lists are internally just compound terms with functor `.`, so they flow through unification, substitution walking, and the engine without special cases. Helper functions make construction and inspection ergonomic for other modules that need to work with lists.

**Acceptance criteria:**
- [ ] `EMPTY_LIST` constant exists and equals `Atom("[]")`
- [ ] `make_list([])` returns `EMPTY_LIST`
- [ ] `make_list([Num(1), Num(2)])` returns a compound term structurally equal to `Compound(".", (Num(1), Compound(".", (Num(2), EMPTY_LIST))))`
- [ ] `list_elements(make_list([a, b, c]))` returns `[a, b, c]`
- [ ] `is_list(EMPTY_LIST)` is True
- [ ] `is_list(Compound(".", (Num(1), Var("T"))))` is False (partial)
- [ ] 6+ unit tests passing
- [ ] No regressions in existing term tests

---

### MINILOG-060 — Lexer support for list syntax tokens

**Description:**
Add new tokens to `minilog/lexer.py` for list surface syntax: `[`, `]`, and `|`. The comma token already exists for compound term argument separation and is reused in list context. The pipe `|` specifically marks the head/tail boundary in `[H|T]` deconstruction patterns and is a new token for minilog.

**What needs to be done:**
- Add three new token kinds: `LBRACKET`, `RBRACKET`, `PIPE`
- Extend the tokenizer to produce these tokens for `[`, `]`, `|` characters
- Ensure `|` is only recognized as `PIPE` in list context; outside lists it is still rejected as an unknown character (to avoid confusion with future uses like disjunction)
- Update lexer tests to cover all three new tokens in isolation and in combination
- Write ≥4 unit tests in `tests/unit/test_lexer_list.py`:
  - Empty list `[]` tokenizes to `LBRACKET, RBRACKET`
  - List with elements `[1, 2, 3]` tokenizes correctly
  - Head-tail pattern `[H|T]` tokenizes to `LBRACKET, IDENT(H), PIPE, IDENT(T), RBRACKET`
  - Nested list `[[1], [2]]` tokenizes correctly with nested brackets

**Dependencies:** MINILOG-059, MINILOG-004

**Expected result:**
The lexer recognizes all three list syntax characters and produces tokens that the parser (MINILOG-061) can consume. No parsing logic yet — just token production.

**Acceptance criteria:**
- [ ] `LBRACKET`, `RBRACKET`, `PIPE` token kinds exist
- [ ] Tokenizing `[1, 2, 3]` produces the expected sequence
- [ ] Tokenizing `[H|T]` produces the expected sequence
- [ ] 4+ unit tests passing
- [ ] No regressions in existing lexer tests

---

### MINILOG-061 — Parser support for list literals and `[H|T]`

**Description:**
Extend `minilog/parser.py` to parse list literal and head-tail patterns into the list representation defined in MINILOG-059. Both syntactic forms desugar into the same dot-functor structure, which means everything after parsing is uniform.

**What needs to be done:**
- Add a new grammar production `list_term` that matches one of three forms:
  - `[]` — empty list, parses to `EMPTY_LIST`
  - `[T1, T2, ..., Tn]` — literal list, parses to `make_list([T1, T2, ..., Tn])`
  - `[T1, T2, ..., Tn | Tail]` — head-tail pattern, parses to nested cons cells with `Tail` as the final rest, i.e. `.(T1, .(T2, .(..., Tail)))`
- Integrate `list_term` into the `term` production so lists can appear anywhere terms are expected: as arguments to compound terms, as heads and bodies of rules, inside queries, inside other lists (nesting)
- Each `T_i` inside the list is itself a full `term`, allowing nesting and mixing of types
- The tail after `|` can be any term, including a variable (for pattern matching), another list, or a compound term
- Proper error messages for malformed lists: unmatched brackets, trailing comma, empty pipe position, multiple pipes
- Write ≥8 unit tests in `tests/unit/test_parser_list.py`:
  - Parse `[]` into `EMPTY_LIST`
  - Parse `[1]` into single-element list
  - Parse `[1, 2, 3]` into 3-element list
  - Parse `[H|T]` into cons with head variable and tail variable
  - Parse `[H1, H2 | T]` into two-element head with tail
  - Parse nested `[[1, 2], [3, 4]]`
  - Parse list inside compound term argument: `батько([авраам, ісак], ?y)`
  - Reject malformed: `[1, 2,]`, `[|T]`, `[1 | 2 | 3]`
- Update existing parser integration tests to verify no regressions

**Dependencies:** MINILOG-060, MINILOG-005

**Expected result:**
The parser produces list terms from both literal and head-tail surface syntax, and lists integrate cleanly with all existing term constructs. Rules can take lists as arguments, deconstruct them through `[H|T]` patterns, and pass them around.

**Acceptance criteria:**
- [ ] All three list forms (`[]`, `[a, b, c]`, `[H|T]`) parse correctly
- [ ] Nested lists parse correctly
- [ ] Lists work as arguments to compound terms
- [ ] Parser integrates list_term into the term production without breaking existing syntax
- [ ] Malformed list syntax produces clear error messages
- [ ] 8+ unit tests passing
- [ ] No regressions in existing parser tests

---

### MINILOG-062 — Unification for list terms

**Description:**
Since lists are represented as compound terms with dot functor, the existing unification algorithm in `minilog/unify.py` already handles them correctly — no changes needed in principle. This issue verifies that assumption through extensive testing, adds any edge-case handling that turns out to be missing, and ensures that partial list unification works correctly (e.g., `[H|T]` against `[1, 2, 3]` binds `H=1` and `T=[2, 3]`).

**What needs to be done:**
- Review `unify.py` to confirm that `Compound` unification handles dot-functor cons cells correctly
- If the existing `unify` function uses structural recursion on `Compound.args`, no code change is needed
- Add an integration smoke test that unifies various list patterns and verifies bindings
- Write ≥10 unit tests in `tests/unit/test_unify_list.py`:
  - `[]` unifies with `[]`
  - `[1]` unifies with `[X]` binding `X=1`
  - `[1, 2, 3]` unifies with `[A, B, C]` binding three variables
  - `[H|T]` unifies with `[1, 2, 3]` binding `H=1`, `T=[2, 3]`
  - `[H|T]` unifies with `[1]` binding `H=1`, `T=[]`
  - `[H|T]` does NOT unify with `[]`
  - `[1, 2 | T]` unifies with `[1, 2, 3, 4]` binding `T=[3, 4]`
  - Nested list unification: `[[X, Y], Z]` unifies with `[[1, 2], [3, 4]]`
  - Occurs check: `X` does not unify with `[1 | X]` if occurs check is enabled
  - Unification of variable with list: `X` unifies with `[1, 2, 3]` binding `X`
- Performance smoke test: unification of two 100-element lists completes in reasonable time

**Dependencies:** MINILOG-059, MINILOG-006

**Expected result:**
List unification works correctly for all common patterns encountered in Prolog programming. No special-case code path needed — lists flow through the existing `Compound` unification machinery.

**Acceptance criteria:**
- [ ] All list unification patterns work as expected
- [ ] `[H|T]` deconstruction binds head and tail correctly
- [ ] Partial matches (multiple pipe elements) work
- [ ] Nested list unification works
- [ ] 10+ unit tests passing
- [ ] No changes to existing unification algorithm (confirmation it Just Works)
- [ ] Performance acceptable for lists up to ~1000 elements

---

### MINILOG-063 — Tracer formatting for lists

**Description:**
Update `minilog/tracer.py` and any other term-formatting code so that list terms are displayed using surface syntax (`[1, 2, 3]` or `[H|T]`) rather than the raw dot-functor representation (`.(1, .(2, .(3, [])))`). This is purely a display concern but critical for usability — without it, every proof tree with a list becomes unreadable.

**What needs to be done:**
- Add a term formatting helper `format_term(term: Term) -> str` that detects list structures and renders them in surface syntax
- Detection logic: if a term is a `Compound` with functor `.` and arity 2, walk the tail:
  - If the tail chain terminates at `[]`, render as `[e1, e2, ..., en]`
  - If the tail chain ends at a variable or non-list term, render as `[e1, e2, ..., en | Rest]`
  - Otherwise fall back to dot-functor representation
- Integrate `format_term` into `tracer.py` for proof tree formatting, into `repl.py` for query result display, and into any other places that show terms to users
- Handle nested lists recursively — inner lists also get surface syntax
- Write ≥6 unit tests in `tests/unit/test_format_list.py`:
  - Empty list renders as `[]`
  - Single-element list renders as `[1]`
  - Multi-element list renders as `[1, 2, 3]`
  - Partial list renders as `[1, 2 | T]` where T is a variable
  - Nested list renders as `[[1, 2], [3, 4]]`
  - Mixed types render correctly: `[авраам, 42, батько(?x)]`

**Dependencies:** MINILOG-062, MINILOG-011

**Expected result:**
Lists display as `[1, 2, 3]` and `[H|T]` everywhere a term is shown to the user: query results, proof trees, error messages, REPL output. The internal representation is unchanged; only display changes.

**Acceptance criteria:**
- [ ] `format_term` detects list structures and uses surface syntax
- [ ] Empty lists render as `[]`
- [ ] Proper lists render with square brackets
- [ ] Partial lists render with pipe notation
- [ ] Nested lists render recursively
- [ ] Proof trees containing lists are readable
- [ ] REPL query results show lists in surface syntax
- [ ] 6+ unit tests passing

---

### MINILOG-064 — Lists core documentation and basic examples

**Description:**
Document lists in `docs/language-reference.md` and create a new example file `examples/lists_basics.ml` demonstrating basic list patterns. This is the user-facing complement to the engine work in MINILOG-059..063 and marks the completion of Phase 15.1.

**What needs to be done:**
- Extend `docs/language-reference.md` with a new section "Списки" (Lists) containing:
  - Introduction to what a list is and why it matters (Ukrainian main text, English technical terms, no emoji)
  - Surface syntax: `[]`, `[1, 2, 3]`, `[H|T]`, `[H1, H2 | T]`, nested lists
  - Internal representation (dot-functor cons cells), with a note that users don't need to worry about this except when debugging
  - How pattern matching on lists works: unification of `[H|T]` with a concrete list binds head and tail
  - A warning that the built-in predicates (`member`, `append`, `length`, etc.) come in Phase 15.2, not in this phase
- Create `examples/lists_basics.ml` with progressive examples:
  - Fact with a list argument: `список_патріархів([авраам, ісак, яків, йосип])`
  - Pattern matching the head: `перший(?H) якщо список_патріархів([?H|?_])`
  - Pattern matching the tail: `хвіст(?T) якщо список_патріархів([?_|?T])`
  - Lists with numbers: `цифри([1, 2, 3, 4, 5])`
  - Nested lists for matrix representation: `матриця([[1, 2], [3, 4]])`
  - Recursive rule that works on lists without needing `member` or `append` yet — for example, "check if list has exactly 3 elements"
- Create `examples/lists_basics.expected.txt` with expected output for queries in the example file
- No integration test required yet — deferred to MINILOG-068 which adds the full stdlib testing

**Dependencies:** MINILOG-063

**Expected result:**
Users can read the language reference, understand how lists work in minilog, and run the basic example file to see lists in action. This is the first minilog example that uses lists natively.

**Acceptance criteria:**
- [ ] `docs/language-reference.md` has a new Lists section
- [ ] Section is in Ukrainian with English technical terms, no emoji
- [ ] `examples/lists_basics.ml` exists and runs without errors
- [ ] `examples/lists_basics.expected.txt` matches actual output
- [ ] Example demonstrates head-tail matching and nested lists
- [ ] Cross-links to Phase 15.2 stdlib section (once that exists)

---

**Phase 15.1 scope notes:**

- Total effort: ~3-4 days (2 × M + 2 × M + 2 × S)
- Strictly sequential by dependency chain: MINILOG-059 first (terms), then 060 (lexer) and 062 (unify) can go in parallel, then 061 (parser) depends on 060, then 063 (tracer) depends on 062, then 064 (docs) depends on 063
- No external dependencies
- New modules created: `tests/unit/test_terms_list.py`, `tests/unit/test_lexer_list.py`, `tests/unit/test_parser_list.py`, `tests/unit/test_unify_list.py`, `tests/unit/test_format_list.py`, `examples/lists_basics.ml`, `examples/lists_basics.expected.txt`
- Existing files modified: `minilog/terms.py`, `minilog/lexer.py`, `minilog/parser.py`, `minilog/unify.py` (possibly, only if needed), `minilog/tracer.py`, `minilog/repl.py` (possibly, for output formatting), `docs/language-reference.md`
- No changes to `minilog/engine.py`, `minilog/kb.py`, `minilog/evaluator.py`, `minilog/forward.py`, `minilog/evolution.py` — lists are purely at the term level and flow through existing machinery

**Acceptance for Phase 15.1 as a whole:**
The user can write rules that take lists as arguments, deconstruct them with `[H|T]` patterns, and query them through the REPL, with results displayed in readable surface syntax. No built-in list predicates yet — those come in Phase 15.2 — but the foundation is in place.

---

## Phase 15.2 — List Built-ins

**Rationale:**
With lists as first-class data type (Phase 15.1), the next step is providing the standard library of list-manipulation predicates that every Prolog programmer expects. `member/2`, `append/3`, `length/2`, `nth0/3`, `reverse/2` — these are the building blocks for nearly every algorithm over collections. This phase implements them as pure minilog rules in a new `minilog/stdlib.ml` file that is auto-loaded by the REPL and CLI.

The key decision is that these predicates are **written in minilog itself** where possible, not as Python built-ins. This keeps the standard library transparent and educational — users can read `stdlib.ml` to see how classical Prolog predicates are defined, which is one of the most instructive experiences in learning logic programming. Only predicates that fundamentally cannot be expressed in pure minilog (like the meta-predicate `findall/3` in Phase 15.3) are implemented in Python.

### MINILOG-065 — `member/2` and `append/3` in stdlib

**Summary:** Create `minilog/stdlib.ml` with the foundational list predicates `member/2` (element-in-list check) and `append/3` (list concatenation). Both are written as pure minilog rules following classical Prolog definitions: `member(X, [X|_])` and `member(X, [_|T]) якщо member(X, T)`, and similarly for append. Test each predicate in both forward mode (check/build) and backward mode (generate/deconstruct) to verify the relational power that lists unlock.

**Size:** S **Dependencies:** MINILOG-064

### MINILOG-066 — `length/2` and `nth0/3` with arithmetic

**Summary:** Add `length/2` (list length) and `nth0/3` (zero-indexed element access) to `stdlib.ml`. Both require Phase 9 arithmetic (MINILOG-024) because they involve counting and indexing. `length` is straightforward recursive accumulation; `nth0` recurses through the list while decrementing the index. Also add `nth1/3` (one-indexed variant) for convenience.

**Size:** M **Dependencies:** MINILOG-065, MINILOG-024

### MINILOG-067 — `last/2`, `reverse/2`, `msort/2` additional predicates

**Summary:** Add three more commonly used list predicates: `last/2` (last element), `reverse/2` (list reversal via accumulator pattern for efficiency), and `msort/2` (sort with duplicates preserved). `msort/2` is the trickiest because sorting requires arithmetic comparisons on elements, but since minilog only supports numeric comparison via `<`/`>`, msort works only on numeric lists in this phase. A full `sort/2` over arbitrary atoms would need term ordering, deferred to a future phase.

**Size:** S **Dependencies:** MINILOG-065

### MINILOG-068 — stdlib documentation and loader mechanism

**Summary:** Implement automatic loading of `stdlib.ml` when the REPL or CLI starts. Add a `--no-stdlib` flag to disable it for tests and educational contexts where users want to see "raw" minilog without library support. Document every stdlib predicate in `docs/language-reference.md` with signature, mode annotations (which arguments can be input vs output), and usage examples. Add integration tests for each predicate in `tests/integration/test_stdlib.py`.

**Size:** S **Dependencies:** MINILOG-067

**Phase 15.2 scope notes:**
- Total effort: ~2-3 days (1 × M + 3 × S)
- Hard prerequisite: Phase 15.1 must be fully merged, plus Phase 9 arithmetic (MINILOG-024) for `length/2` and `nth0/3`
- New files: `minilog/stdlib.ml`, `tests/integration/test_stdlib.py`
- Existing files modified: `minilog/repl.py` and `minilog/cli.py` (auto-load stdlib), `docs/language-reference.md` (stdlib section)
- Phase 15.2 acceptance: `member(2, [1, 2, 3])` returns true, `append([1, 2], [3, 4], L)` returns `L = [1, 2, 3, 4]`, `length([a, b, c], N)` returns `N = 3`, all running from the REPL without explicit file loading

---

## Phase 15.3 — Meta-predicates

**Rationale:**
Meta-predicates — predicates that take other goals as arguments and control their evaluation — are what make Prolog practical for anything beyond small examples. `findall/3` is the single most important meta-predicate: it collects all solutions to a query into a list, which enables patterns like "give me all my ancestors", "find all books older than 1900", "enumerate every valid graph coloring". Without `findall`, users are stuck pressing `;` in the REPL to see solutions one at a time, with no way to work with the complete set programmatically.

This phase implements `findall/3` in Python inside `engine.py` as a special form (not a rule, because meta-predicates fundamentally need to control the inner query evaluation). It also adds `bagof/3` and `setof/3`, which are refinements of `findall` with different failure semantics and result ordering.

### MINILOG-069 — `findall/3` engine implementation

**Summary:** Implement `findall(Template, Goal, List)` as a special form in `engine.py`. When the solver encounters `findall/3`, it creates a fresh substitution, runs `Goal` in a nested solve loop, collects every successful `Template` instantiation, and unifies `List` with the resulting list. Must handle variable scoping correctly so inner variables don't leak into outer query. Must always succeed, returning `[]` for queries with zero solutions (unlike `bagof` which fails). Include tests for common patterns: collecting all parents, collecting with nested conditions, collecting with arithmetic filters.

**Size:** M **Dependencies:** MINILOG-064, MINILOG-009

### MINILOG-070 — `bagof/3` and `setof/3`

**Summary:** Add `bagof/3` (collect with group-by on free variables, fails on zero solutions) and `setof/3` (same as bagof but sorts and removes duplicates). These are implemented on top of `findall/3` with additional logic. `bagof` is trickier because of the existential quantifier notation `^` which lets users say "ignore this variable for grouping purposes", but for minilog's educational goals a simplified version without `^` is acceptable. `setof` requires a term ordering for deduplication and sorting — numeric ordering only for MVP, deferring full term ordering.

**Size:** M **Dependencies:** MINILOG-069

### MINILOG-079 — `call/N` and `forall/2` meta-predicates

**Summary:** Add two more meta-predicates that complete the classical Prolog set. `call(Goal)` takes a term and executes it as a query, enabling higher-order programming where goals are passed as arguments. `call/N` is variadic: `call(Goal, X1, X2, ..., Xn)` extends `Goal` with additional arguments before executing, so `call(member, E, List)` is equivalent to `member(E, List)`. Support `call/1` through `call/7` to cover all practical patterns (Goal plus up to 6 extra arguments). `forall(Cond, Action)` is defined as "for every solution of Cond, Action must also succeed" — semantically equivalent to `\+ (Cond, \+ Action)`. Both are implemented as special forms in `engine.py`: `call/N` constructs a new Compound term from the Goal and extra arguments, then solves it; `forall/2` iterates through Cond solutions and verifies Action for each. Include tests for both predicates in standalone use and in combination with `findall/3`, `member/2`, and typical classification patterns.

**Size:** M **Dependencies:** MINILOG-069

### MINILOG-071 — Meta-predicates documentation

**Summary:** Extend `docs/language-reference.md` with a Meta-predicates section covering the five new predicates (`findall`, `bagof`, `setof`, `call/N`, `forall`), their differences, mode annotations, and common use patterns. Include examples showing why `findall` is more commonly used than `bagof`/`setof` in practice, and how `call` enables higher-order programming patterns impossible without it. Add a warning about non-declarative aspects: meta-predicates have subtle interaction with the engine that users should understand. Include a worked example showing how `forall/2` expresses "all X in list satisfy predicate P" more naturally than building an accumulator loop.

**Size:** S **Dependencies:** MINILOG-079

**Phase 15.3 scope notes:**
- Total effort: ~2-3 days (3 × M + 1 × S)
- Dependency: Phase 15.1 and 15.2 must be complete
- Modifies `minilog/engine.py` to add special-form handling for all five meta-predicates
- Phase 15.3 acceptance: `findall(X, parent(X, joseph), Ancestors)` returns a list of all parents of joseph; `call(member, 2, [1, 2, 3])` succeeds as if `member(2, [1, 2, 3])` were called directly; `forall(member(X, [1, 2, 3]), X > 0)` succeeds because all list elements are positive

---

## Phase 15.4 — Small Built-ins

**Rationale:**
Two small features that are independent of lists and meta-predicates but often requested: the classical `var/1`/`nonvar/1` type inspection predicates, and an extension to the existing `не` negation so it can accept conjunctions of goals (not just single atoms). Both are cheap to implement and useful for writing tic-tac-toe-style examples where "check if cell is empty" needs explicit handling.

### MINILOG-072 — Type inspection: `var`, `nonvar`, `atom`, `number`, `ground`

**Summary:** Add a family of Python-level type-inspection built-ins covering all common patterns from classical Prolog. `var(X)` succeeds if X is an unbound variable; `nonvar(X)` succeeds if X is bound to a concrete term; `atom(X)` succeeds if X is an atom; `number(X)` succeeds if X is a numeric literal (integer or float); `ground(X)` succeeds if X contains no unbound variables anywhere in its structure (recursive check through compound terms). All five are thin wrappers around `walk` from `unify.py` plus isinstance checks against the term classes in `terms.py`. Document the non-declarative nature clearly: these predicates' success depends on evaluation order and the current substitution state, not just logical meaning. Include unit tests for each predicate in isolation and combined patterns (e.g., `ground(батько(авраам, ?x))` fails because `?x` is unbound). Usage pattern note: `ground/1` is especially useful as a guard before arithmetic comparisons or I/O-like operations to ensure all arguments are fully instantiated.

**Size:** S **Dependencies:** MINILOG-009

### MINILOG-073 — Extended negation for conjunctions

**Summary:** Extend the parser to accept `не (goal1 і goal2 і ...)` with parentheses and conjunctions inside, and update `engine.py` to handle the extended form. Currently `Negation.inner` only supports a single `Compound`; this change allows it to be a list of goals that are solved as a conjunction inside the negation. This matches classical Prolog `\+` behavior and enables patterns like `\+ (member(X, List), forbidden(X))`.

**Size:** S **Dependencies:** MINILOG-009

**Phase 15.4 scope notes:**
- Total effort: ~1 day (2 × S)
- Independent of Phase 15.1-15.3 — can be implemented at any point after MINILOG-009
- Small, contained changes to parser and engine
- Phase 15.4 acceptance: `var(X)` succeeds on unbound X; `не (батько(?x, ?y) і вік(?x, ?a) і ?a > 50)` parses and evaluates correctly

---

## Phase 15.5 — Advanced Examples

**Rationale:**
After Phase 15.1-15.4 are complete, minilog has all the building blocks needed for classical Prolog examples that were impossible in Phase 1: lists, list manipulation predicates, meta-predicates for collecting solutions, var/nonvar for mode-aware predicates, and proper negation over conjunctions. Phase 15.5 delivers four flagship examples that showcase these capabilities and prove that minilog has grown from an educational toy into a working Prolog capable of real classical programming.

Each example in this phase is **generic** over input size, unlike the Phase 1 combinatorial examples (`graph_coloring.ml`, `hamiltonian_path.ml`, `school_schedule.ml`) which had fixed arity. The generic versions demonstrate why lists matter: a single rule works for graphs of any size, boards of any dimension, problems of any scale.

### MINILOG-074 — Generic graph coloring example

**Summary:** Create `examples/graph_coloring_generic.ml` which uses lists to represent graphs and colors generically. The graph is a list of vertex-neighbors pairs, colors are a list, assignment is a list of vertex-color pairs. The coloring predicate recurses through the vertex list, for each vertex picks a color from the color list, and checks that no neighbor already has the same color. Uses `member/2`, `nth0/3`, and recursion on list tails. Demonstrates the difference from Phase 1 `graph_coloring.ml`: generic over graph size, no fixed arity, one rule handles all cases. Include expected output for 3-4 test graphs.

**Size:** M **Dependencies:** MINILOG-068, MINILOG-069

### MINILOG-075 — Generic hamiltonian path example

**Summary:** Create `examples/hamiltonian_path_generic.ml` using lists for vertices and path accumulation. The path is built through recursive list construction: at each step, pick a neighbor of the current end that is not yet in the path, append it, recurse. Uses `member/2` for the "not yet visited" check and `append/3` for path extension. Demonstrates contrast with Phase 1 fixed-arity version. Test on 3-5 graphs of increasing size.

**Size:** M **Dependencies:** MINILOG-068, MINILOG-069

### MINILOG-076 — Tic-tac-toe example with winning moves

**Summary:** Create `examples/tic_tac_toe.ml` with board represented as a 9-element list where each cell is either `x`, `o`, or an unbound variable (using `var/1` to detect empty cells). Predicates: `wins/2` (check if player has won), `make_move/4` (place player symbol at index), `winning_move/3` (find move that wins immediately via backtracking), `blocking_move/3` (find move that blocks opponent from winning), `best_move/3` (priority: winning, then blocking, then any empty). Demonstrates `var/1`, list-based board representation, and backtracking-driven search. Does not implement full minimax (which would require much deeper rules), but covers the practical "expert beginner" level of play.

**Size:** M **Dependencies:** MINILOG-068, MINILOG-069, MINILOG-072

### MINILOG-077 — N-queens example

**Summary:** Create `examples/n_queens.ml` which solves the classical N-queens problem using lists. Queens represented as a list where the i-th element is the column of the queen in row i. Safety check verifies that no two queens attack each other through column sharing, diagonal sharing, or anti-diagonal sharing. The `solve/2` predicate takes board size N and returns a valid placement. Using `findall/3`, can also return all solutions. Demonstrates generic combinatorial search over variable-size input, which was impossible in Phase 1. Expected output covers N=4, N=5, N=6 with solution counts matching known results (2, 10, 4 solutions respectively).

**Size:** M **Dependencies:** MINILOG-068, MINILOG-069

### MINILOG-078 — Phase 15 advanced examples documentation

**Summary:** Create `docs/phase15-advanced-examples.md` walking through each of the four new examples, explaining the algorithms, showing how lists and meta-predicates enable them, and contrasting with the Phase 1 fixed-arity equivalents. This is the capstone document of Phase 15 and serves as the main educational artifact showing what lists unlock. Include a section on "before and after": side-by-side comparison of Phase 1 `graph_coloring.ml` (130 lines, fixed arity) and Phase 15 `graph_coloring_generic.ml` (expected ~40 lines, any size). Update `README.md` with mention of the new examples.

**Size:** S **Dependencies:** MINILOG-077

**Phase 15.5 scope notes:**
- Total effort: ~4-5 days (4 × M + 1 × S)
- Dependency: Phases 15.1, 15.2, 15.3 must be complete; Phase 15.4 optional but recommended for tic-tac-toe
- No changes to `minilog/` core modules — this phase is purely additive content
- Four new example files plus four `.expected.txt` files
- One new documentation file
- Phase 15.5 acceptance: all four example files run to completion and produce expected output; documentation explains each example and links from README

---

## Phase 15.6 — Syntax Extensions

**Rationale:**
After Phases 15.1-15.5 give minilog the data structures and predicates of a working Prolog, Phase 15.6 adds syntactic conveniences that make the language more natural to read and write. Two features: disjunction through the Ukrainian keyword `або` (as counterpart to the existing `і` for conjunction), and user-defined infix operators through the classical `op/3` directive. Both are purely syntactic — they desugar into constructs that already exist in minilog — but both have significant impact on how naturally a knowledge base reads.

The original "Conscious Limitations" document rejected disjunction and custom operators on the grounds that they were "syntactic sugar without educational value". That rejection was reconsidered: disjunction through `або` matches the conjunction-through-`і` pattern that minilog already uses, and custom operators enable natural-language-like syntax (`сократ є людина`) that makes minilog read as a genuine knowledge representation language rather than a formal system. Both are Phase 15 additions precisely because by then the educational core is already in place — users understand how backtracking works over explicit alternatives, so compact disjunction syntax does not hide any mechanics.

### MINILOG-080 — Disjunction operator `або`

**Summary:** Add Ukrainian keyword `або` as a binary infix operator in rule bodies, forming the disjunctive counterpart to the existing `і` conjunction operator. Parse `A або B` into a new `Disjunction` AST node with two branches. The engine handles `Disjunction` by trying the left branch first and, on failure or on backtracking, trying the right branch — equivalent to having two separate rules with the same head. Supports parentheses for grouping: `A і (B або C) і D`. Operator precedence: `або` binds looser than `і` (so `A і B або C і D` parses as `(A і B) або (C і D)`), matching classical Prolog semantics for `,` vs `;`. Include parser tests for operator precedence, nesting, and interaction with negation (`не (A або B)`). Engine tests verify that disjunction produces the same solutions as the equivalent split-rule formulation. Does not introduce any new Python machinery beyond a new AST class and a solve case in `engine.py`.

**Size:** S **Dependencies:** MINILOG-005

### MINILOG-081 — Custom infix operators via `op/3` directive

**Summary:** Implement user-defined infix operators through a `op/3` directive at the top of `.ml` files, following classical Prolog convention. Syntax: `:- op(Priority, Fixity, Name).` where Priority is an integer from 1 to 1200 (lower = tighter binding), Fixity is one of `xfx`, `xfy`, `yfx` (binary operators with different associativity), and Name is the operator atom. Example directive: `:- op(700, xfx, є).` declares `є` as a non-associative binary operator with precedence 700. After this directive, `сократ є людина` parses exactly as `є(сократ, людина)`. Scope: binary infix operators only (no prefix `fx`/`fy` or postfix `xf`/`yf` in this phase, to keep parser changes manageable). Implementation requires an operator precedence parser alongside the existing recursive descent parser — when the parser encounters a term, it consults the current operator table and uses precedence climbing to parse operator expressions. Operator table is maintained per-file and reset at start of each file load. Built-in operators (`і`, `або`, `не`, `=`, `≠`, `<`, `≤`, `>`, `≥`) are pre-loaded into the default table but can be overridden. Include substantial test coverage: each fixity type, precedence interactions, operator overloading, ambiguity handling, error messages for malformed operator declarations.

**Size:** L **Dependencies:** MINILOG-080

### MINILOG-082 — Phase 15.6 syntax extensions documentation

**Summary:** Extend `docs/language-reference.md` with a Syntax Extensions section covering disjunction and custom operators. Document the precedence and associativity of built-in operators in a reference table. Provide a worked example showing how custom operators transform a knowledge base from compound-term syntax to natural-language-like syntax, e.g., comparing `є(сократ, людина), смертна(людина)` against `сократ є людина, людина смертна`. Create `examples/natural_syntax.ml` demonstrating a philosophical/ontological knowledge base written with custom operators (`є`, `має`, `належить`) and corresponding `natural_syntax.expected.txt`. Update README with mention of the syntax extensions as an optional style.

**Size:** S **Dependencies:** MINILOG-081

**Phase 15.6 scope notes:**
- Total effort: ~2-3 days (1 × S + 1 × L + 1 × S)
- MINILOG-081 is the largest issue in Phase 15 by complexity because operator precedence parsing is non-trivial
- Purely parser-level changes; engine has minimal additions (just the `Disjunction` AST handling)
- Phase 15.6 acceptance: `p :- a або b` parses and executes correctly; `:- op(700, xfx, є). сократ є людина.` parses as compound term `є(сократ, людина)`; `examples/natural_syntax.ml` runs successfully

---

## Phase 15.7 — String Manipulation

**Rationale:**
minilog already has a `Str` term type (strings appear in facts like `підпис(марко, "Капітан пошти")`) but offers no operations over strings beyond storage and equality. Phase 15.7 adds the essential string manipulation predicates that unlock real text processing: length, concatenation, character-level access, case transformation, substring extraction, and splitting. All predicates operate on the existing `Str` type — this is variant A from the design discussion, chosen because the type already exists and is the cleanest representation.

The scope is deliberately limited to predicates that are trivially implementable as Python wrappers around Python's own string operations. No regex (out of scope, requires a separate subsystem), no format strings (I/O-adjacent), no Unicode normalization (complex, rare need). The goal is to make text-label manipulation ergonomic for use cases like building display names, extracting filename extensions, splitting CSV-like data, validating prefixes and suffixes — the everyday 80% of string work that appears in practical rules.

### MINILOG-083 — String core predicates: length, concat, chars

**Summary:** Add three foundational string predicates as Python built-ins operating on the existing `Str` term type. `string_length(S, N)` computes the length of string S (in characters, not bytes) as integer N. `string_concat(S1, S2, S3)` concatenates S1 and S2 into S3, and in reverse mode can split S3 into all possible S1/S2 pairs through backtracking (matching classical Prolog semantics). `string_chars(S, L)` converts between a string and a list of single-character strings, requiring Phase 15.1 lists as well. All three implemented as special forms in `engine.py` that recognize the specific functor and delegate to Python's built-in string operations. Include tests for forward mode (build result), check mode (verify result matches), and where applicable reverse mode (backtrack through splits). Document edge cases: empty strings, single-character strings, mixed-case strings.

**Size:** M **Dependencies:** MINILOG-009

### MINILOG-084 — String transformations: upper, lower, sub_string, split

**Summary:** Add higher-level string predicates on top of the core built-ins. `string_upper(S, U)` converts S to all-uppercase as U; `string_lower(S, L)` converts to lowercase. `sub_string(S, Start, Length, Sub)` extracts a substring starting at position `Start` with given `Length`, returning `Sub`. In forward mode with Start and Length given, deterministic; in search mode with Sub given and Start/Length unbound, backtracks through all occurrences of Sub in S (returning each as a separate solution). `split_string(S, SepChars, PadChars, Parts)` splits S into a list of parts using any character in `SepChars` as separator, stripping `PadChars` from each part. All implemented as Python built-ins delegating to Python string methods with careful mode handling. Include tests for each predicate, especially the multi-mode behavior of `sub_string` which enables substring-search patterns.

**Size:** M **Dependencies:** MINILOG-083, MINILOG-064

### MINILOG-085 — Phase 15.7 string manipulation documentation

**Summary:** Extend `docs/language-reference.md` with a String Manipulation section documenting all seven string predicates with signatures, mode annotations, and practical examples. Create `examples/string_basics.ml` demonstrating typical patterns: building a full name from first/last parts, extracting a file extension, counting characters in a sentence, splitting CSV-like data into fields, case-insensitive comparison through `string_lower`, verifying prefix/suffix. Corresponding `string_basics.expected.txt` with expected query outputs. Update README to mention string support as part of Phase 15 deliverables.

**Size:** S **Dependencies:** MINILOG-084

**Phase 15.7 scope notes:**
- Total effort: ~2-3 days (2 × M + 1 × S)
- Depends only on existing `Str` type plus Phase 15.1 lists (for `string_chars` and `split_string`)
- No core engine changes beyond special-form dispatch
- Phase 15.7 acceptance: `string_length("hello", N)` returns `N = 5`; `string_concat("foo", "bar", S)` returns `S = "foobar"`; `split_string("a,b,c", ",", "", Parts)` returns `Parts = ["a", "b", "c"]`; `examples/string_basics.ml` runs successfully

---

## Phase 15.8 — Feature Examples

**Rationale:**
Phases 15.1-15.7 add features to minilog; Phase 15.8 demonstrates them. Each example file isolates one new capability and shows it in a small, realistic scenario, then the final example combines multiple features in a single integrated showcase. The goal is pedagogical: a new user who has read the language reference can run these examples one by one and see each feature "in motion" before writing their own rules.

This phase is intentionally the last one: it depends on (almost) everything that came before. Individual examples have narrower dependencies and can be started as soon as their specific prerequisites are met — MINILOG-086 needs only disjunction (15.6), MINILOG-088 needs only type inspection (15.4), etc. The integrated showcase (MINILOG-091) is the only one that genuinely requires most of Phase 15 to be in place.

All examples follow the established minilog convention: Ukrainian main text with English technical terms in comments, no emoji, `.ml` source file with matching `.expected.txt`, placed in `examples/` directory. Traced queries may appear in `.ml` files but are omitted from `.expected.txt` because proof tree variable suffixes are runtime-dependent.

### MINILOG-086 — Example: disjunction in family relations

**Summary:** Create `examples/disjunction_family.ml` demonstrating the `або` disjunction operator in a family-tree knowledge base. Contains biblical patriarchs as facts (батько/мати relations), defines `родич/2` both with and without disjunction (two variants: `родич_старий` using two rules, `родич` using one rule with `або`), and includes more complex rules showing `або` mixed with `і` (conjunction) with explicit parentheses for grouping. Queries should demonstrate semantic equivalence between the two styles and showcase how `або` reads naturally in Ukrainian. Include corresponding `.expected.txt` file with expected query outputs. This is the simplest Phase 15.8 example and serves as the introduction to disjunction for users coming from the fixed-arity Phase 1 examples.

**Size:** S **Dependencies:** MINILOG-080

### MINILOG-087 — Example: natural-syntax ontology with custom operators

**Summary:** Create `examples/natural_syntax_ontology.ml` demonstrating custom infix operators in an Aristotelian/philosophical knowledge base. Uses `:- op(700, xfx, є).`, `:- op(700, xfx, має).`, `:- op(700, xfx, належить).` to declare natural-language infix operators. Facts read as natural prose: `сократ є людина`, `людина має смертність`, `людина належить біологія`. Rules demonstrate operator usage in both head and body positions: `?x є ?z якщо ?x є ?y і ?y є ?z`. Transitivity of `є` and property inheritance through `є` chain. Queries showcase natural-language syllogisms like "Socrates is mortal" derivation. Include `.expected.txt`. This example targets domain experts from philosophy/ontology backgrounds and demonstrates how custom operators make minilog accessible beyond programmers.

**Size:** M **Dependencies:** MINILOG-081

### MINILOG-088 — Example: polymorphic describe via type inspection

**Summary:** Create `examples/type_inspection_polymorphic.ml` demonstrating all type inspection predicates (`var`, `nonvar`, `atom`, `number`, `ground`) through a `опис/2` predicate that classifies any term into a human-readable category. Multiple clauses for `опис` with different type guards, ordered from most specific (var) to most general (compound). Also includes examples of `ground/1` as a guard before arithmetic operations to ensure all variables are bound. Demonstrates the non-declarative nature of type predicates by showing how query order affects results. Include queries that pass atoms, numbers, unbound variables, partially ground compounds, and fully ground compounds, with expected `.expected.txt` outputs. Educational note in comments about mode-aware programming.

**Size:** S **Dependencies:** MINILOG-072

### MINILOG-089 — Example: higher-order programming via `call/N` and `forall`

**Summary:** Create `examples/higher_order_programming.ml` demonstrating `call/N` and `forall/2` meta-predicates in classical higher-order programming patterns. Implements `map/3` (apply predicate to every list element), `filter/3` (keep elements satisfying a predicate), `усі_задовольняють/2` (all elements satisfy a predicate) via both recursive style with `call/N` and declarative style with `forall/2`. Uses simple test predicates (`позитивне/1`, `парне/1`, `більше_за/2`) as arguments to higher-order predicates. Shows how `call(предикат, аргумент)` enables passing predicates as data, the core insight of higher-order programming. Include queries that map, filter, and test lists of numbers, with `.expected.txt`. Educational note about how this was impossible in Phase 1 without meta-predicates.

**Size:** M **Dependencies:** MINILOG-079, MINILOG-064

### MINILOG-090 — Example: text processing with string predicates

**Summary:** Create `examples/string_processing.ml` demonstrating all Phase 15.7 string manipulation predicates in practical text-processing tasks. Predicates implemented: `повне_ім'я/3` (build full name from first and last parts), `довгий_рядок/1` (check if string length exceeds threshold), `розпарсити_csv/2` (split comma-separated line into fields using `split_string`), `починається_з/2` (prefix check using `sub_string`), `містить/2` (substring search using `sub_string` in search mode), `нормалізувати/2` (case normalization via `string_lower`), `ініціали/2` (extract first characters from full name via `string_chars`). Include realistic test data: names, email addresses, CSV lines. Include `.expected.txt`. Educational note about how the existing `Str` type (which was only storable before Phase 15.7) now becomes a working data type with a full operations library.

**Size:** M **Dependencies:** MINILOG-084

### MINILOG-091 — Example: integrated library catalog showcase

**Summary:** Create `examples/library_catalog.ml` as the integrated showcase example combining multiple Phase 15 features in a single realistic scenario: a library catalog knowledge base. Uses custom operators (`:- op(700, xfx, автор). :- op(700, xfx, рік). :- op(700, xfx, жанр).`) so that facts read as `"Гамлет" автор "Шекспір"`, `"Гамлет" рік 1603`. Rules use disjunction to handle alternative queries (by author OR by year range), `findall/3` to collect result sets, `sub_string` to search by title substring, `ground/1` to validate query arguments, and `forall/2` to check catalog-wide invariants. Demonstrates 5+ Phase 15 features working together in ~80 lines of expressive minilog. Queries: search by author, find books in year range, collect all books matching a title substring, check catalog consistency. Include `.expected.txt`. This is the capstone example showing what Phase 15 enables and contrasts sharply with Phase 1 examples like `mythology.ml` that had the same domain complexity but much more verbose expression.

**Size:** M **Dependencies:** MINILOG-081, MINILOG-080, MINILOG-069, MINILOG-084

### MINILOG-092 — Phase 15.8 feature examples documentation

**Summary:** Create `docs/phase15-feature-examples.md` as a walkthrough of all six Phase 15.8 example files, explaining which features each demonstrates, pedagogical notes, and cross-references between examples. Include a feature matrix table showing which Phase 15 features (disjunction, custom operators, type inspection, meta-predicates, strings) appear in which examples. Update `README.md` to mention the feature showcase examples as a recommended tour after Phase 1 basics. Include notes on progression: start with MINILOG-086 (simplest, single feature) and end with MINILOG-091 (most complex, multiple features). This is the capstone document of Phase 15.8 and, together with the Phase 15.5 advanced examples documentation, forms the complete educational path through Phase 15.

**Size:** S **Dependencies:** MINILOG-091

**Phase 15.8 scope notes:**
- Total effort: ~5-7 days (4 × M + 3 × S)
- Pure content phase — no changes to minilog core modules
- Creates 6 new example files + 6 `.expected.txt` files + 1 documentation file
- Individual examples have narrow dependencies and can start as soon as their specific prerequisites are met; does not require all of Phase 15.1-15.7 to be complete before some examples can begin
- Phase 15.8 acceptance: all example files run to completion after their dependencies are implemented; documentation explains each example and provides cross-links from README; feature matrix clearly shows coverage of all new Phase 15 features

---

## Overall Estimate

| Phase | Issues | Effort | Deliverable |
|---|---|---|---|
| Phase 15.1 — Lists Core | 6 | 3-4 days | Lists as first-class term type with parser, unify, tracer support |
| Phase 15.2 — List Built-ins | 4 | 2-3 days | `stdlib.ml` with member, append, length, nth0, reverse, etc. |
| Phase 15.3 — Meta-predicates | 4 | 2-3 days | `findall/3`, `bagof/3`, `setof/3`, `call/N`, `forall/2` in engine |
| Phase 15.4 — Small Built-ins | 2 | 1 day | type inspection (var/nonvar/atom/number/ground), extended negation |
| Phase 15.5 — Advanced Examples | 5 | 4-5 days | Generic coloring, hamiltonian, tic-tac-toe, N-queens, docs |
| Phase 15.6 — Syntax Extensions | 3 | 2-3 days | Disjunction `або`, custom infix operators via `op/3`, docs |
| Phase 15.7 — String Manipulation | 3 | 2-3 days | String core predicates, transformations, docs |
| Phase 15.8 — Feature Examples | 7 | 5-7 days | Six example files plus documentation showcasing every new feature |
| **Total** | **34** | **~21-27 days** | minilog transformed into a working Prolog with natural syntax and full feature showcase |

---

## Explicitly Rejected

**Cut (`!`).** The classical Prolog cut operator is not included in Phase 15. Rationale: cut breaks declarative semantics by making rule order meaningful, which is a direct contradiction of minilog's pedagogical goal of teaching pure logic programming. Users who need deterministic rule selection can achieve it through guard conditions that make rules mutually exclusive. The absence of cut is a deliberate design choice, not an oversight.

**If-then-else (`->`).** The classical Prolog `Cond -> Then ; Else` operator is not included. Same rationale: it is a non-declarative construct that breaks the logic programming model. Users can express conditionals through multiple rules with mutually exclusive guards.

**`assert/1` and `retract/1`.** Dynamic modification of the knowledge base during query evaluation is not included. These predicates violate the logical reading of a Prolog program and are considered harmful even in classical Prolog literature. minilog remains a pure logic language with an immutable knowledge base.

**Full term ordering for `sort/2`.** Phase 15 only provides `msort/2` over numeric lists. A full `sort/2` over arbitrary terms would require defining a total order over atoms, compounds, numbers, and lists — a significant design decision deferred to a future phase.

**DCG (Definite Clause Grammars).** The `-->` operator and DCG translation are not included. DCGs are a classical Prolog feature for parsing, but they require syntactic sugar and a compile-time transformation that is out of scope for Phase 15. Users who want to do parsing can write rules manually using the list infrastructure.

All of these could be added in future phases if there is demand, but none of them are required for the examples and use cases Phase 15 aims to support.

---

## Relationship to Other Phases

**Phase 15 depends on Phase 1 (core engine) and Phase 9 (arithmetic).** Specifically, `length/2` and `nth0/3` require arithmetic for index computation, so the Phase 15.2 `MINILOG-066` issue has an explicit hard dependency on `MINILOG-024`.

**Phase 15 is independent of Phase 10 (geometry), Phase 11-14 (text extraction), and the Phase 9 calculator extension (MINILOG-058).** All of these can proceed in parallel with Phase 15 once their own prerequisites are met.

**Phase 15 is a prerequisite for any future phase that wants to do serious symbolic computation** over structured data: full parser implementation, symbolic differentiation, theorem proving, constraint logic programming, etc. These are all classical Prolog applications that become possible only after lists exist.

**Relationship to minilog as an educational tool.** Phase 15 is the transition point where minilog stops being "a toy for understanding Prolog basics" and becomes "a working Prolog that can solve real problems". The examples in 15.5 (generic graph algorithms, N-queens, tic-tac-toe) are the same ones used in classical Prolog textbooks, which means students who learn minilog can transfer their knowledge directly to SWI-Prolog or other full implementations.

---

**Document status:** draft for review. Phase 15.1 issues are fully detailed. Phases 15.2-15.7 are captured at high level (one-paragraph summaries per issue); they will be expanded to full Description / What needs to be done / Acceptance criteria format as each phase approaches implementation.

**Revision history:**
- Initial version: 20 issues across Phases 15.1-15.5 (Lists Core, List Built-ins, Meta-predicates, Small Built-ins, Advanced Examples)
- Expansion 2026-04 (iteration 1): added 7 issues across new Phases 15.6 (Syntax Extensions: disjunction `або`, custom operators via `op/3`) and 15.7 (String Manipulation: length/concat/chars/transformations). Extended MINILOG-072 scope to cover full type inspection family (var/nonvar/atom/number/ground). Added MINILOG-079 (call/N and forall/2) to Phase 15.3. Total after iteration 1: 27 issues, ~16-20 days effort.
- Expansion 2026-04 (iteration 2): added Phase 15.8 — Feature Examples (7 new issues MINILOG-086..092) with illustrative example files for each new feature from Phases 15.3, 15.4, 15.6, 15.7, plus an integrated showcase combining multiple features. Total after iteration 2: 34 issues, ~21-27 days effort.

**No code changes made. Plan only.**
