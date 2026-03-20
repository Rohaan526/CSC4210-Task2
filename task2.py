from __future__ import annotations

import argparse
import sys

from kmap import format_groupings, format_kmap
from logic_core import (
    TruthRow,
    build_truth_table,
    canonical_pos,
    canonical_sop,
    default_variable_names,
    format_truth_table,
    maxterms,
    minterms,
    parse_bit,
    parse_csv_truth_table,
    simplify_pos,
    simplify_sop,
    validate_simplified_expression,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Truth Table -> Boolean Equation -> K-Map Simplification"
    )
    parser.add_argument("--vars", type=int, help="Number of input variables (n >= 2)")
    parser.add_argument("--mode", choices=("sop", "pos"), default="sop", help="Canonical form to generate")
    parser.add_argument("--input", help="Path to a CSV truth table")
    parser.add_argument("--interactive", action="store_true", help="Enter the truth table interactively")
    return parser


def interactive_truth_table(n_vars: int | None, mode: str):
    if n_vars is None:
        n_vars = int(input("Number of input variables (n >= 2): ").strip())
    if n_vars < 2:
        raise ValueError("The number of input variables must be at least 2.")

    default_names = default_variable_names(n_vars)
    raw_names = input(
        f"Variable names separated by spaces [{', '.join(default_names)}]: "
    ).strip()
    if raw_names:
        normalized_names = [name.strip() for name in raw_names.replace(",", " ").split() if name.strip()]
        variable_names = tuple(normalized_names)
    else:
        variable_names = tuple(default_names)
    if len(variable_names) != n_vars:
        raise ValueError(f"Expected {n_vars} variable names, received {len(variable_names)}.")

    row_count = 2 ** n_vars
    print(f"Enter {row_count} rows as {', '.join(variable_names)}, out using only 0 or 1.")
    rows = []
    for index in range(row_count):
        raw = input(f"Row {index + 1}/{row_count}: ").replace(",", " ").split()
        if len(raw) != n_vars + 1:
            raise ValueError(f"Each row must contain {n_vars + 1} binary values.")
        bits = tuple(parse_bit(value, f"row {index + 1} input") for value in raw[:-1])
        output = parse_bit(raw[-1], f"row {index + 1} output")
        rows.append(TruthRow(bits, output))

    return build_truth_table(variable_names, rows)


def render_report(table, mode: str) -> str:
    if mode == "sop":
        canonical = canonical_sop(table)
        indices = minterms(table)
        simplified, implicants = simplify_sop(table)
        symbol = "m"
    else:
        canonical = canonical_pos(table)
        indices = maxterms(table)
        simplified, implicants = simplify_pos(table)
        symbol = "M"

    lines = [
        "Truth table",
        format_truth_table(table),
        "",
        f"Canonical equation ({mode.upper()})",
        canonical,
        "",
        "Minterm / Maxterm list",
        f"{symbol}({', '.join(str(index) for index in indices)})" if indices else f"{symbol}()",
        "",
        "K-Map",
    ]

    if table.n_vars <= 4:
        lines.append(format_kmap(table))
    else:
        lines.append("K-map rendering skipped because the assignment limits K-map work to 2-4 variables.")

    lines.extend(
        [
            "",
            "K-Map grouping",
            format_groupings(implicants, table, mode),
            "",
            "Simplified Boolean expression",
            simplified,
            "",
            "Validation result",
            "PASS" if validate_simplified_expression(table, mode, implicants) else "FAIL",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input and not args.interactive:
        parser.error("Provide either --input or --interactive.")
    if args.input and args.interactive:
        parser.error("Use either --input or --interactive, not both.")
    if args.vars is not None and args.vars < 2:
        parser.error("--vars must be at least 2.")

    try:
        if args.input:
            table = parse_csv_truth_table(args.input, expected_n_vars=args.vars)
        else:
            table = interactive_truth_table(args.vars, args.mode)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(render_report(table, args.mode))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
