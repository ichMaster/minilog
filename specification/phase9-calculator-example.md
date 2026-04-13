# minilog Phase 9 Extension — Calculator / AST Walker Example

## Issues Summary Table

| # | ID | Title | Size | Phase | Dependencies |
|---|---|---|---|---|---|
| 58 | MINILOG-058 | Calculator example: AST walker with arithmetic evaluation | M | 9 — Calculator Extension | MINILOG-024 |
| 59 | MINILOG-059 | Add `!=` as alias for `≠` comparison operator | S | 9 — Calculator Extension | None |
| 60 | MINILOG-060 | Deduplicate query results in CLI and REPL output | S | 9 — Calculator Extension | None |

**Size legend:** S = ≤ 0.5 day, M = 0.5–1 day, L = 1–2 days

---

## Rationale

Phase 9 adds arithmetic expressions to minilog (MINILOG-021..024): lexer support for `+`, `-`, `*`, `/`, parser support for expressions inside comparison goals, evaluator support for compound arithmetic terms and built-in functions (`sqrt`, `abs`, `pow`). Once that work is complete, minilog gains the ability to compute numeric values from nested expressions.

This unlocks a classic Prolog pedagogical example that is impossible in Phase 1: an **AST walker** — a set of rules that traverse a parse tree represented as compound terms and compute a numeric value at the root. In traditional Prolog this is one of the first exercises taught alongside list processing; for minilog without lists, the structural recursion happens on compound terms directly, which is arguably cleaner and easier to read.

The example demonstrates three ideas that the existing minilog example set does not cover:

1. **Structural recursion on compound terms.** Every other example in `examples/` (family, biology, recipes, mythology, terra_tacita, geometry) uses flat facts and shallow rules. The calculator recurses into nested compound terms via unification patterns like `бін(?op, ?l, ?r)`, which is the core idiom for working with tree-shaped data in Prolog
2. **Separation of syntax and semantics.** The parse tree itself is just data — a compound term. The evaluator rules interpret that data. This is the same pattern used in real compilers and interpreters, and it makes the example a natural bridge from minilog to more serious symbolic computation
3. **Practical use of Phase 9 arithmetic.** Arithmetic in minilog exists to be used, not just demonstrated in a small smoke test. The calculator is a realistic consumer of `+`, `-`, `*`, `/`, `sqrt`, `pow`, and `abs` — it shows how these pieces compose

The example is a **pure consumer of Phase 9 arithmetic** and a **demonstration of compound term recursion**. It does not require lists, DCG, or any other extension beyond what Phase 9 delivers. That makes it the natural first post-Phase-9 example and the right place to validate that the arithmetic implementation actually supports real use cases.

---

## MINILOG-058 — Calculator example: AST walker with arithmetic evaluation

**Description:**
Create a complete example package (`examples/calculator.ml`, `examples/calculator.expected.txt`, and a companion document `docs/calculator-explained.md`) demonstrating a small AST walker that evaluates arithmetic expressions represented as nested compound terms. The example is a consumer of Phase 9 arithmetic: it uses `+`, `-`, `*`, `/`, `sqrt`, `pow`, and `abs` from inside rule bodies to compute numeric values recursively.

The example teaches three things that no existing minilog example covers: structural recursion on compound terms, the separation between a parse tree as data and the rules that interpret it, and realistic composition of Phase 9 arithmetic features.

**Design notes (locked before implementation):**

1. **No parser — the AST is given.** The example does not turn a string like `"1+2*3"` into a tree. That would require lexer/parser work over token streams, which minilog does not yet support cleanly without lists. Instead, the parse tree is provided as compound-term facts. The user assembles trees by writing them out explicitly, the evaluator interprets them. This keeps the focus on the walker pattern, not on parsing
2. **Tree representation.** Three node types, all compound terms:
   - `число(N)` — a leaf holding a numeric constant
   - `бін(?op, ?l, ?r)` — a binary node with operator `?op` (one of `плюс`, `мінус`, `множення`, `ділення`) and two subtree children
   - `функція(?name, ?arg)` — a unary function node with name (`sqrt`, `abs`) or `функція_pow(?base, ?exp)` for two-argument `pow`
3. **Evaluator as rules.** A predicate `обчислити(?tree, ?value)` that unifies the tree against each shape and recursively computes the value of subtrees. Phase 9 arithmetic handles the actual numeric work; the rules just dispatch on tree shape
4. **Named example trees.** Several trees are stored as facts with names, for example `вираз(ex1, бін(плюс, число(1), бін(множення, число(2), число(3)))).`. This lets queries look up trees by name and evaluate them, and keeps the example readable
5. **Query patterns covered:**
   - Evaluate a named expression: `?- вираз(ex1, ?t) і обчислити(?t, ?v).` expects `?v = 7`
   - Evaluate multiple expressions and compare: find all named expressions whose value is greater than 10
   - Structural queries that do not evaluate but inspect shape: count the number of binary operators in a tree, find leaves, check whether a tree is a pure constant expression (no variables — trivially true in this example since there are no variables, but the pattern is instructive)
   - Traced evaluation query showing the recursive proof tree for a small expression — this demonstrates that the walker is a real recursive computation, not a lookup
6. **Edge cases to cover in the example:**
   - Division by zero must raise `EvaluatorError` from Phase 9 evaluator and should be demonstrated with a deliberately failing query plus a comment explaining the behavior
   - Nested functions: `sqrt(pow(3, 2) + pow(4, 2))` evaluating to `5.0` — the Pythagorean distance expressed as an AST
   - Negative intermediate results handled correctly by `abs`
7. **Language and style:**
   - Ukrainian identifiers and comments throughout (to match existing examples)
   - English technical terms where appropriate (`AST`, `walker`, `evaluator`)
   - No emoji anywhere
   - File length target: 100–150 lines for the `.ml` file, comparable to `biology.ml` and the planned `geometry_triangles.ml`

**What needs to be done:**

- Create `examples/calculator.ml` with:
  - Multi-line `%` header comment explaining what the example demonstrates, the design choice to provide the AST as facts rather than parse it, and a link to `docs/calculator-explained.md`
  - Operator constants as facts: `оператор(плюс).`, `оператор(мінус).`, `оператор(множення).`, `оператор(ділення).`
  - The core evaluator predicate `обчислити/2` implemented as one rule per node shape:
    - `правило обчислити(число(?n), ?n).` — leaf case, the value of a number node is the number itself
    - `правило обчислити(бін(плюс, ?l, ?r), ?v) якщо обчислити(?l, ?lv) і обчислити(?r, ?rv) і ?v = ?lv + ?rv.` — binary plus
    - Similar rules for `мінус`, `множення`, `ділення`
    - `правило обчислити(функція(sqrt, ?a), ?v) якщо обчислити(?a, ?av) і ?v = sqrt(?av).` — unary function call
    - Similar rule for `abs`
    - `правило обчислити(функція_pow(?base, ?exp), ?v) якщо обчислити(?base, ?bv) і обчислити(?exp, ?ev) і ?v = pow(?bv, ?ev).` — binary function call
  - 6–10 named example trees as facts with progressive complexity:
    - `ex1`: simple constant `число(42)` → 42
    - `ex2`: basic sum `бін(плюс, число(1), число(2))` → 3
    - `ex3`: precedence `бін(плюс, число(1), бін(множення, число(2), число(3)))` → 7
    - `ex4`: nested subtraction `бін(мінус, бін(плюс, число(10), число(5)), число(3))` → 12
    - `ex5`: division with float result `бін(ділення, число(10), число(4))` → 2.5
    - `ex6`: Pythagorean distance `функція(sqrt, бін(плюс, функція_pow(число(3), число(2)), функція_pow(число(4), число(2))))` → 5.0
    - `ex7`: absolute value of negative `функція(abs, бін(мінус, число(3), число(10)))` → 7
    - `ex8`: division by zero `бін(ділення, число(1), число(0))` — will fail at evaluation
  - A structural predicate `є_листком/1` that checks whether a tree is a leaf: `правило є_листком(число(?n)).`
  - A structural predicate `бінарний_вузол/1` that matches any binary node shape: `правило бінарний_вузол(бін(?op, ?l, ?r)).`
  - A set of queries demonstrating both evaluation and structural inspection:
    - Evaluate each of ex1..ex7 and print the result (8 queries total)
    - Try to evaluate ex8 (deliberate division by zero, expected error — documented in a comment)
    - Structural query: `?- вираз(?name, ?t) і є_листком(?t).` — find all named expressions that are pure leaves (only ex1)
    - Structural query: `?- вираз(?name, ?t) і бінарний_вузол(?t).` — find all named expressions whose root is a binary node
    - Traced query: `?- слід обчислити(бін(плюс, число(1), число(2)), ?v).` showing the recursive proof tree
  - End-of-file summary comment listing the concepts demonstrated and cross-linking to `docs/calculator-explained.md` and to the Phase 9 arithmetic section of `docs/language-reference.md`
- Create `examples/calculator.expected.txt`:
  - Hand-computed expected output for every non-traced query
  - Follow the same format conventions as `family.expected.txt` and `graph_coloring.expected.txt`
  - The traced query output is **not included** (following the convention established for `graph_coloring.ml` and `hamiltonian_path.ml`), because the proof tree contains runtime-dependent variable suffixes. The traced query remains in the `.ml` file for interactive use but is omitted from the expected output
  - The division-by-zero query should produce an `EvaluatorError` in actual output; the expected file handles this either by explicitly including the error line or by documenting in a header comment that this query is expected to raise. The implementer should pick whichever matches the minilog REPL's actual behavior at the time of writing
- Create `docs/calculator-explained.md` (~6–8 pages, Ukrainian main text with English technical terms, no emoji):
  - **Introduction:** what an AST walker is, why this pattern matters, relationship to real compilers and interpreters
  - **The parse tree as data:** the three node shapes (`число`, `бін`, `функція`/`функція_pow`), why compound terms are a natural fit for trees, contrast with list-based representations used in classical Prolog
  - **Structural recursion:** how each rule of `обчислити/2` matches one node shape and recursively evaluates subtrees. Walk through the proof tree for `ex3` (1 + 2 * 3) step by step, showing unification and the order of recursive calls
  - **Phase 9 arithmetic in action:** explicit discussion of how `?v = ?lv + ?rv` inside a rule body uses the new Phase 9 infrastructure (lexer tokens, parser expression rules, evaluator recursive walk). Cross-link to `language-reference.md` arithmetic section
  - **Separation of syntax and semantics:** the parse tree is just data; the rules interpret it. If we wanted a symbolic differentiator instead of an evaluator, we would write a different predicate over the same tree shape. This is the decoupling compilers use
  - **Edge cases and error handling:** division by zero, negative arguments to `sqrt`, why these raise `EvaluatorError` from Phase 9 rather than silently failing
  - **Structural vs evaluative queries:** the difference between asking "what is the value of this tree" and "what shape does this tree have." Show that `є_листком/1` and `бінарний_вузол/1` inspect structure without triggering evaluation
  - **Limitations of this example:**
    - No parser: you write the tree by hand, minilog does not turn a string into a tree
    - No variables in expressions: every `число` holds a concrete constant. Symbolic expressions with variables would require a substitution environment, which is a separate exercise
    - No operator precedence handling: that is done by the user when they build the tree, not by the evaluator. Real compilers handle precedence in the parser
  - **Where to go next:** pointers to classical Prolog textbooks covering parser construction, DCG grammars, and symbolic computation. Note that a full parser-in-minilog would need lists or a custom indexing scheme, and is out of scope for Phase 9
- Update `docs/language-reference.md`:
  - Add `calculator.ml` to the "Приклади" section with a one-paragraph description
  - Cross-link to `docs/calculator-explained.md`
  - Note that this example requires Phase 9 arithmetic
- Update `README.md`:
  - Add mention of `calculator.ml` to the examples list
  - One-sentence description: "AST walker that evaluates arithmetic expressions represented as compound terms, demonstrating structural recursion and Phase 9 arithmetic"
- Write an integration test `tests/integration/test_calculator.py` following the same pattern as other example integration tests, comparing `minilog run examples/calculator.ml` output against `examples/calculator.expected.txt`. Handle the traced query the same way other tests do (either skip byte-for-byte comparison on the traced block or use normalized diff that strips variable suffixes)

**Dependencies:** MINILOG-024

Phase 9 arithmetic must be fully merged and operational. Specifically:
- MINILOG-021 (lexer tokens for `+`, `-`, `*`, `/`)
- MINILOG-022 (parser support for arithmetic expressions in comparison goals)
- MINILOG-023 (evaluator support for compound arithmetic terms and `sqrt`, `abs`, `pow`)
- MINILOG-024 (documentation and basic demo)

Without MINILOG-023, the rule body `?v = ?lv + ?rv` cannot be evaluated and the example cannot run.

**Expected result:**

A new example package that is the first real consumer of Phase 9 arithmetic, demonstrates structural recursion on compound terms (a pattern no existing minilog example covers), and gives users a concrete bridge from the toy arithmetic demo in MINILOG-024 to a realistic use case. The companion document explains both the walker pattern and how it composes with Phase 9 arithmetic, serving as a reference for anyone building their own tree-shaped data processing in minilog.

**Acceptance criteria:**

- [ ] `examples/calculator.ml` parses without errors and runs to completion
- [ ] All non-error queries (ex1..ex7, structural queries) produce the expected values
- [ ] The division-by-zero query (ex8) either raises a visible `EvaluatorError` or is handled consistently with how minilog reports evaluator errors
- [ ] `ex6` (Pythagorean distance via `sqrt(pow(3,2) + pow(4,2))`) evaluates to `5.0`, proving that nested functions and arithmetic compose correctly
- [ ] Structural queries `є_листком/1` and `бінарний_вузол/1` return the correct named expressions without triggering evaluation side effects
- [ ] Traced query produces a visible proof tree with recursive `обчислити` calls and arithmetic comparison goals in the leaves
- [ ] `examples/calculator.expected.txt` matches actual output for all non-traced queries
- [ ] `docs/calculator-explained.md` exists, is in Ukrainian with English technical terms, has no emoji, and covers all sections listed in the design notes
- [ ] `language-reference.md` and `README.md` cross-link to the new example
- [ ] Integration test passes
- [ ] File length: 100–150 lines for `.ml`, ~400–500 markdown lines for the companion doc

---

**Phase 9 Calculator Extension scope notes:**

- Single issue, Size M (~0.5–1 day of work)
- Hard prerequisite: Phase 9 Arithmetic Expressions block (MINILOG-021..024) fully merged
- Affects only `examples/`, `docs/`, `tests/integration/`, and small additions to `language-reference.md` and `README.md`
- No changes to any file under `minilog/` — this is purely an additive example package
- No new external dependencies

**Relationship to other phases:**

- This issue is an **extension** of Phase 9, not a new phase. It lives in its own spec file (`phase9-calculator-example.md`) for clarity, but conceptually belongs to the Phase 9 deliverable set as a capstone example
- It is **independent of Phase 10** (geometry): both are consumers of Phase 9 arithmetic, but neither depends on the other. They can be implemented in parallel once Phase 9 is complete
- It is **independent of Phases 11–14** (text extraction): the calculator example has nothing to do with the extraction workflow and does not interact with the `knowledge_bases/` folder structure

**After this issue is merged,** minilog has a demonstrable AST walker example that proves Phase 9 arithmetic is useful beyond trivial smoke tests, and users have a reference pattern for building their own tree-shaped data processors in minilog.

---

## MINILOG-059 — Add `!=` as alias for `≠` comparison operator

**Description:**
Add `!=` as an alternative syntax for the `≠` (not-equal) comparison operator. Users frequently type `!=` out of habit from other languages, and the `≠` character is hard to type on most keyboards.

**What needs to be done:**

- Add `!=` token recognition in `minilog/lexer.py` mapping to the same `OP_NE` token type as `≠`
- Ensure the parser and evaluator handle it identically to `≠`
- Update tests to cover `!=` syntax
- Update `docs/language-reference.md` to document `!=` as an alias for `≠`

**Dependencies:** None (can be done independently)

**Expected result:**
Both `≠` and `!=` work as the not-equal operator in rules and queries.

**Acceptance criteria:**

- [ ] `?x != ?y` parses and evaluates identically to `?x ≠ ?y`
- [ ] Existing `≠` syntax continues to work unchanged
- [ ] Unit test covers `!=` in a comparison goal
- [ ] Language reference documents the alias

---

## MINILOG-060 — Deduplicate query results in CLI and REPL output

**Description:**
When the same variable bindings are produced multiple times (e.g. because a rule matches via different internal paths that yield the same visible result), the CLI and REPL currently print every duplicate. For example, `?- рідні(Юра, ?x).` prints `?x = Ліда.` twice when Юра and Ліда share two parents. Users expect unique results.

**What needs to be done:**

- In `minilog/cli.py` `_execute_query`: track the set of already-printed binding tuples; skip duplicates
- In `minilog/repl.py` `_execute_query`: same deduplication logic
- Only deduplicate the visible bindings (query variables resolved to ground terms), not the internal substitution — two substitutions that resolve to the same user-visible output are considered duplicates
- Report the deduplicated count in `(N solutions)`
- Add a unit/integration test that verifies deduplication

**Dependencies:** None (can be done independently)

**Expected result:**
Each unique combination of query variable bindings is printed exactly once.

**Acceptance criteria:**

- [ ] A query that previously produced duplicate visible bindings now prints each unique binding set once
- [ ] The solution count reflects unique solutions, not raw engine matches
- [ ] Existing tests continue to pass (expected output files may need updating)
- [ ] At least one test explicitly covers the deduplication behavior

---

**Document status:** draft for review.
**No code changes made. Plan only.**
