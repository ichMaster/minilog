"""Command-line interface for minilog."""

import argparse
import sys

from minilog import __version__
from minilog.errors import MinilogError
from minilog.parser import parse


def cmd_version(_args: argparse.Namespace) -> None:
    """Print version string."""
    print(f"minilog {__version__}")


def cmd_run(args: argparse.Namespace) -> None:
    """Load a .ml file and execute every query in it."""
    from minilog.engine import solve
    from minilog.kb import KnowledgeBase
    from minilog.tracer import Tracer
    from minilog.unify import Substitution

    source = _read_file(args.file)
    program = parse(source)

    kb = KnowledgeBase()
    for fact in program.facts:
        kb.add_fact(fact)
    for rule in program.rules:
        kb.add_rule(rule)

    for query in program.queries:
        _execute_query(query, kb, solve, Tracer(), Substitution)


def cmd_check(args: argparse.Namespace) -> None:
    """Parse-only syntax check; exits 0 on success, 1 on error."""
    source = _read_file(args.file)
    try:
        parse(source)
        print(f"OK: {args.file}")
    except MinilogError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def cmd_repl(args: argparse.Namespace) -> None:
    """Start the interactive REPL."""
    from minilog.repl import Repl

    repl = Repl()
    if args.file:
        repl.load_file(args.file)
    repl.run()


def _read_file(path: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _execute_query(query, kb, solve, tracer, Substitution) -> None:
    """Execute a single query and print results."""
    from minilog.terms import Var

    if query.trace:
        count = 0
        for subst, proof_node in tracer.trace_solve(query.goal, kb):
            print(proof_node.format_tree())
            _print_bindings(query.goal, subst)
            count += 1
        if count == 0:
            print("false.")
        else:
            print(f"({count} solution{'s' if count != 1 else ''})")
    else:
        count = 0
        for subst in solve(query.goal, kb):
            _print_bindings(query.goal, subst)
            count += 1
        if count == 0:
            print("false.")
        else:
            print(f"({count} solution{'s' if count != 1 else ''})")


def _collect_vars(term) -> list:
    """Collect all variables in a term, in order of appearance."""
    from minilog.terms import Compound, Var

    if isinstance(term, Var):
        return [term]
    if isinstance(term, Compound):
        result = []
        for arg in term.args:
            result.extend(_collect_vars(arg))
        return result
    return []


def _print_bindings(goal, subst) -> None:
    """Print variable bindings from a substitution, only for query variables."""
    from minilog.terms import Var

    query_vars = _collect_vars(goal)
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


def main() -> None:
    """Entry point for the minilog CLI."""
    parser = argparse.ArgumentParser(
        prog="minilog",
        description="minilog — a mini-Prolog engine with Ukrainian-language syntax",
    )
    parser.add_argument("--version", action="version", version=f"minilog {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    # run
    run_parser = subparsers.add_parser("run", help="Load a .ml file and execute queries")
    run_parser.add_argument("file", help="Path to a .ml file")
    run_parser.set_defaults(func=cmd_run)

    # repl
    repl_parser = subparsers.add_parser("repl", help="Start the interactive shell")
    repl_parser.add_argument("file", nargs="?", default=None, help="Optional .ml file to pre-load")
    repl_parser.set_defaults(func=cmd_repl)

    # check
    check_parser = subparsers.add_parser("check", help="Parse-only syntax check")
    check_parser.add_argument("file", help="Path to a .ml file")
    check_parser.set_defaults(func=cmd_check)

    # version (also as subcommand for backward compat)
    version_parser = subparsers.add_parser("version", help="Print version")
    version_parser.set_defaults(func=cmd_version)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except MinilogError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
