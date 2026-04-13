"""Interactive REPL for minilog."""

import sys

from minilog import __version__
from minilog.engine import solve
from minilog.errors import MinilogError
from minilog.evolution import run_generations
from minilog.forward import saturate
from minilog.kb import KnowledgeBase
from minilog.parser import parse
from minilog.tracer import Tracer
from minilog.unify import Substitution

try:
    import readline  # noqa: F401 — enables command history
except ImportError:
    pass


HELP_TEXT = """\
Commands:
  :help                — list commands
  :quit | :q           — exit
  :load <file>         — load a .ml file into the current KB
  :stats               — show KB statistics with per-predicate breakdown
  :list <functor>/N    — list all facts and rules for a predicate
  :evolve <N>          — run N generations of production rules
  :saturate            — run forward chaining to fixpoint
  :trace on|off        — toggle automatic tracing
  :kb                  — dump the entire knowledge base (facts and rules)
  :clear               — wipe the KB

Any other line is interpreted as a fact, rule, or query."""


class Repl:
    """Interactive minilog shell."""

    def __init__(self) -> None:
        self.kb = KnowledgeBase()
        self.tracer = Tracer()
        self.trace_mode = False

    def run(self) -> None:
        """Main REPL loop."""
        print(f"minilog {__version__} — type :help for commands, :quit to exit")
        while True:
            try:
                line = input("minilog> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break

            line = line.strip()
            if not line:
                continue

            if line.startswith(":"):
                if self._handle_command(line):
                    break
            else:
                self._handle_input(line)

    def load_file(self, path: str) -> None:
        """Load a .ml file into the KB."""
        try:
            with open(path, encoding="utf-8") as f:
                source = f.read()
        except FileNotFoundError:
            print(f"Error: file not found: {path}")
            return
        except OSError as e:
            print(f"Error: {e}")
            return

        try:
            program = parse(source)
        except MinilogError as e:
            print(str(e))
            return

        for fact in program.facts:
            self.kb.add_fact(fact)
        for rule in program.rules:
            self.kb.add_rule(rule)
        if program.production_rules:
            for pr_def in program.production_rules:
                self.kb.add_production_rule(self._build_production_rule(pr_def))

        stats = self.kb.stats()
        parts = [f"{stats['facts']} facts", f"{stats['rules']} rules"]
        if stats['production_rules'] > 0:
            parts.append(f"{stats['production_rules']} production rules")
        print(f"Loaded {path}: {', '.join(parts)}")

    def _handle_command(self, line: str) -> bool:
        """Handle a colon-prefixed command. Returns True to quit."""
        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in (":quit", ":q"):
            return True

        if cmd == ":help":
            print(HELP_TEXT)
        elif cmd == ":load":
            if not arg:
                print("Usage: :load <file>")
            else:
                self.load_file(arg)
        elif cmd == ":stats":
            self._cmd_stats()
        elif cmd == ":list":
            self._cmd_list(arg)
        elif cmd == ":evolve":
            self._cmd_evolve(arg)
        elif cmd == ":saturate":
            added = saturate(self.kb)
            print(f"Saturated: {added} new facts derived")
        elif cmd == ":trace":
            self._cmd_trace(arg)
        elif cmd == ":kb":
            self._cmd_kb()
        elif cmd == ":clear":
            self.kb = KnowledgeBase()
            print("Knowledge base cleared.")
        else:
            print(f"Unknown command: {cmd}. Type :help for available commands.")

        return False

    def _cmd_stats(self) -> None:
        """Show KB statistics with per-predicate breakdown."""
        stats = self.kb.stats()
        parts = [f"Facts: {stats['facts']}", f"Rules: {stats['rules']}"]
        if stats['production_rules'] > 0:
            parts.append(f"Production rules: {stats['production_rules']}")
        parts.append(f"Predicates: {stats['predicates']}")
        print(", ".join(parts))
        for functor, arity, fact_count, rule_count in self.kb.predicates():
            parts = []
            if fact_count > 0:
                parts.append(f"{fact_count} fact{'s' if fact_count != 1 else ''}")
            if rule_count > 0:
                parts.append(f"{rule_count} rule{'s' if rule_count != 1 else ''}")
            print(f"  {functor}/{arity} ({', '.join(parts)})")

    def _cmd_kb(self) -> None:
        """Dump the entire knowledge base grouped by predicate."""
        preds = self.kb.predicates()
        if not preds:
            print("Knowledge base is empty.")
            return
        first = True
        for functor, arity, _, _ in preds:
            if not first:
                print()
            first = False
            print(f"% {functor}/{arity}")
            facts, rules = self.kb.lookup(functor, arity)
            for fact in facts:
                print(f"  {fact.head}.")
            for rule in rules:
                body_str = ", ".join(repr(g) for g in rule.body)
                print(f"  {rule.head} :- {body_str}.")
        # Production rules
        pr_rules = self.kb.production_rules()
        if pr_rules:
            if preds:
                print()
            print("% Production rules")
            for pr in pr_rules:
                parts = [f"продукція {pr.name}"]
                if pr.add:
                    parts.append(f"додати {', '.join(repr(t) for t in pr.add)}")
                if pr.remove:
                    parts.append(f"видалити {', '.join(repr(t) for t in pr.remove)}")
                print(f"  {' '.join(parts)}")

    @staticmethod
    def _build_production_rule(pr_def):
        """Convert ProductionRuleDef (parser) to ProductionRule (evolution)."""
        from minilog.evolution import ProductionRule
        # For conjunctive conditions, use the first goal as the main condition
        # The engine will solve the full body via solve_body
        condition = pr_def.condition[0] if len(pr_def.condition) == 1 else pr_def.condition[0]
        return ProductionRule(
            name=pr_def.name,
            condition=condition,
            add=pr_def.add,
            remove=pr_def.remove,
            guard=pr_def.guard,
            body=pr_def.condition,
        )

    def _cmd_list(self, arg: str) -> None:
        """List facts and rules for a predicate."""
        if "/" not in arg:
            print("Usage: :list <functor>/N")
            return
        try:
            functor, arity_str = arg.rsplit("/", 1)
            arity = int(arity_str)
        except ValueError:
            print("Usage: :list <functor>/N (N must be an integer)")
            return

        facts, rules = self.kb.lookup(functor, arity)
        if not facts and not rules:
            print(f"No entries for {functor}/{arity}")
            return
        for fact in facts:
            print(f"  {fact.head}.")
        for rule in rules:
            body_str = ", ".join(repr(g) for g in rule.body)
            print(f"  {rule.head} :- {body_str}.")

    def _cmd_evolve(self, arg: str) -> None:
        """Run N generations of production rules."""
        from minilog.evolution import run_generations as evolve_run
        try:
            n = int(arg) if arg else 1
        except ValueError:
            print("Usage: :evolve <N> (N must be a positive integer)")
            return
        if n <= 0:
            print("Usage: :evolve <N> (N must be positive)")
            return
        if n > 10000:
            print(f"Warning: capping at 10000 generations (requested {n})")
            n = 10000

        rules = self.kb.production_rules()
        if not rules:
            print("No production rules in the knowledge base. Load a file with 'продукція' declarations.")
            return

        try:
            history = evolve_run(self.kb, rules, n)
        except MinilogError as e:
            print(f"Error during evolution: {e}")
            return

        total_added = 0
        total_removed = 0
        for entry in history:
            gen = entry["generation"]
            a = entry["added"]
            r = entry["removed"]
            total_added += len(a)
            total_removed += len(r)
            if not a and not r:
                print(f"  Generation {gen + 1}: no changes (fixpoint reached)")
                break
            parts = []
            if a:
                parts.append(f"+{len(a)} fact{'s' if len(a) != 1 else ''}")
            if r:
                parts.append(f"-{len(r)} fact{'s' if len(r) != 1 else ''}")
            print(f"  Generation {gen + 1}: {', '.join(parts)}")

        executed = len(history)
        print(f"Done. {executed} generation{'s' if executed != 1 else ''} executed, "
              f"{total_added} added, {total_removed} removed.")

    def _cmd_trace(self, arg: str) -> None:
        """Toggle trace mode."""
        if arg.lower() == "on":
            self.trace_mode = True
            print("Trace mode: on")
        elif arg.lower() == "off":
            self.trace_mode = False
            print("Trace mode: off")
        else:
            print("Usage: :trace on|off")

    def _handle_input(self, line: str) -> None:
        """Parse and handle a fact, rule, or query."""
        # Ensure the line ends with a dot
        if not line.endswith("."):
            line += "."

        try:
            program = parse(line)
        except MinilogError as e:
            print(str(e))
            return

        for fact in program.facts:
            self.kb.add_fact(fact)
            print(f"Added fact: {fact.head}.")

        for rule in program.rules:
            self.kb.add_rule(rule)
            print(f"Added rule: {rule.head} :- ...")

        for query in program.queries:
            self._execute_query(query)

    def _execute_query(self, query) -> None:
        """Execute a query and print results."""
        from minilog.terms import Var

        use_trace = query.trace or self.trace_mode
        try:
            if use_trace:
                count = 0
                for subst, proof_node in self.tracer.trace_solve(query.goal, self.kb):
                    print(proof_node.format_tree())
                    self._print_bindings(query.goal, subst)
                    count += 1
                if count == 0:
                    print("false.")
                else:
                    print(f"({count} solution{'s' if count != 1 else ''})")
            else:
                count = 0
                seen_bindings: set[tuple] = set()
                for subst in solve(query.goal, self.kb):
                    key = self._binding_key(query.goal, subst)
                    if key in seen_bindings:
                        continue
                    seen_bindings.add(key)
                    self._print_bindings(query.goal, subst)
                    count += 1
                if count == 0:
                    print("false.")
                else:
                    print(f"({count} solution{'s' if count != 1 else ''})")
        except MinilogError as e:
            print(str(e))

    def _print_bindings(self, goal, subst) -> None:
        """Print variable bindings from a substitution, only for query variables."""
        from minilog.terms import Compound, Var

        query_vars = self._collect_vars(goal)
        printed = False
        seen = set()
        for var in query_vars:
            if var.name == "_":
                continue
            if var.name in seen:
                continue
            seen.add(var.name)
            resolved = subst.apply(var)
            if resolved != var:
                print(f"?{var.name} = {resolved}.")
                printed = True
        if not printed:
            print("true.")

    def _binding_key(self, goal, subst) -> tuple:
        """Compute a hashable key from the visible bindings for deduplication."""
        query_vars = self._collect_vars(goal)
        parts = []
        seen = set()
        for var in query_vars:
            if var.name == "_" or var.name in seen:
                continue
            seen.add(var.name)
            resolved = subst.apply(var)
            parts.append((var.name, repr(resolved)))
        return tuple(parts)

    @staticmethod
    def _collect_vars(term) -> list:
        """Collect all variables in a term, in order of appearance."""
        from minilog.terms import Compound, Var

        if isinstance(term, Var):
            return [term]
        if isinstance(term, Compound):
            result = []
            for arg in term.args:
                result.extend(Repl._collect_vars(arg))
            return result
        return []
