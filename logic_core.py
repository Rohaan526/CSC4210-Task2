from __future__ import annotations

import csv
from itertools import combinations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TruthRow:
    inputs: tuple[int, ...]
    output: int


@dataclass(frozen=True)
class TruthTable:
    variable_names: tuple[str, ...]
    rows: tuple[TruthRow, ...]

    @property
    def n_vars(self) -> int:
        return len(self.variable_names)

    @property
    def sorted_rows(self) -> list[TruthRow]:
        return sorted(self.rows, key=lambda row: row.inputs)


@dataclass(frozen=True)
class Implicant:
    values: tuple[int | None, ...]
    covered_indices: frozenset[int]

    def combine(self, other: "Implicant") -> "Implicant | None":
        diff_count = 0
        merged: list[int | None] = []
        for left, right in zip(self.values, other.values):
            if left == right:
                merged.append(left)
                continue
            if left is None or right is None:
                return None
            diff_count += 1
            if diff_count > 1:
                return None
            merged.append(None)
        if diff_count != 1:
            return None
        return Implicant(tuple(merged), self.covered_indices | other.covered_indices)

    def literal_count(self) -> int:
        return sum(value is not None for value in self.values)


def default_variable_names(n_vars: int) -> list[str]:
    names: list[str] = []
    for index in range(n_vars):
        base = chr(ord("A") + (index % 26))
        suffix = "" if index < 26 else str(index // 26)
        names.append(f"{base}{suffix}")
    return names


def parse_csv_truth_table(path: str | Path, expected_n_vars: int | None = None) -> TruthTable:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file is missing a header row.")
        fieldnames = [field.strip() for field in reader.fieldnames]
        if len(fieldnames) < 3:
            raise ValueError("CSV header must contain at least two input columns and one output column.")
        if fieldnames[-1].lower() != "out":
            raise ValueError("CSV header must end with an 'out' column.")

        variable_names = fieldnames[:-1]
        if expected_n_vars is not None and len(variable_names) != expected_n_vars:
            raise ValueError(
                f"CSV defines {len(variable_names)} input columns but --vars was {expected_n_vars}."
            )

        rows: list[TruthRow] = []
        for line_number, raw_row in enumerate(reader, start=2):
            normalized = {key.strip(): (value or "").strip() for key, value in raw_row.items()}
            inputs: list[int] = []
            for variable_name in variable_names:
                if variable_name not in normalized:
                    raise ValueError(f"Line {line_number}: missing value for {variable_name}.")
                inputs.append(parse_bit(normalized[variable_name], f"Line {line_number} column {variable_name}"))
            output = parse_bit(normalized.get(fieldnames[-1], ""), f"Line {line_number} column out")
            rows.append(TruthRow(tuple(inputs), output))

    table = TruthTable(tuple(variable_names), tuple(rows))
    validate_truth_table(table)
    return table


def parse_bit(raw_value: str, context: str) -> int:
    if raw_value not in {"0", "1"}:
        raise ValueError(f"{context} must be 0 or 1, got {raw_value!r}.")
    return int(raw_value)


def build_truth_table(variable_names: Iterable[str], rows: Iterable[TruthRow]) -> TruthTable:
    table = TruthTable(tuple(variable_names), tuple(rows))
    validate_truth_table(table)
    return table


def validate_truth_table(table: TruthTable) -> None:
    if table.n_vars < 2:
        raise ValueError("The number of input variables must be at least 2.")

    expected_rows = 2 ** table.n_vars
    if len(table.rows) != expected_rows:
        raise ValueError(f"Truth table must contain exactly {expected_rows} rows for {table.n_vars} variables.")

    seen_inputs: set[tuple[int, ...]] = set()
    for row in table.rows:
        if len(row.inputs) != table.n_vars:
            raise ValueError("Each row must contain a value for every input variable.")
        for bit in row.inputs:
            if bit not in {0, 1}:
                raise ValueError("Input values must be 0 or 1.")
        if row.output not in {0, 1}:
            raise ValueError("Output values must be 0 or 1.")
        if row.inputs in seen_inputs:
            raise ValueError(f"Duplicate input combination found: {row.inputs}.")
        seen_inputs.add(row.inputs)

    expected_combinations = {
        tuple((index >> shift) & 1 for shift in range(table.n_vars - 1, -1, -1))
        for index in range(expected_rows)
    }
    missing = sorted(expected_combinations - seen_inputs)
    if missing:
        raise ValueError(f"Truth table is missing input combinations: {missing}.")


def inputs_to_index(bits: tuple[int, ...]) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def minterms(table: TruthTable) -> list[int]:
    return [inputs_to_index(row.inputs) for row in table.sorted_rows if row.output == 1]


def maxterms(table: TruthTable) -> list[int]:
    return [inputs_to_index(row.inputs) for row in table.sorted_rows if row.output == 0]


def canonical_sop(table: TruthTable) -> str:
    indices = minterms(table)
    if not indices:
        return "0"
    return " + ".join(
        product_term(index_to_bits(index, table.n_vars), table.variable_names) for index in indices
    )


def canonical_pos(table: TruthTable) -> str:
    indices = maxterms(table)
    if not indices:
        return "1"
    return " * ".join(
        sum_term(index_to_bits(index, table.n_vars), table.variable_names) for index in indices
    )


def index_to_bits(index: int, width: int) -> tuple[int, ...]:
    return tuple((index >> shift) & 1 for shift in range(width - 1, -1, -1))


def product_term(bits: tuple[int, ...], variable_names: Iterable[str]) -> str:
    pieces = [
        variable if bit == 1 else f"{variable}'"
        for variable, bit in zip(variable_names, bits)
    ]
    return "".join(pieces)


def sum_term(bits: tuple[int, ...], variable_names: Iterable[str]) -> str:
    pieces = [
        variable if bit == 0 else f"{variable}'"
        for variable, bit in zip(variable_names, bits)
    ]
    return "(" + " + ".join(pieces) + ")"


def prime_implicants(indices: Iterable[int], n_vars: int) -> list[Implicant]:
    current = [Implicant(index_to_bits(index, n_vars), frozenset({index})) for index in sorted(set(indices))]
    primes: set[Implicant] = set()

    while current:
        next_level: set[Implicant] = set()
        used: set[Implicant] = set()
        grouped: dict[int, list[Implicant]] = {}
        for implicant in current:
            ones_count = sum(bit == 1 for bit in implicant.values if bit is not None)
            grouped.setdefault(ones_count, []).append(implicant)

        for ones_count in sorted(grouped):
            left_group = grouped.get(ones_count, [])
            right_group = grouped.get(ones_count + 1, [])
            for left in left_group:
                for right in right_group:
                    combined = left.combine(right)
                    if combined is not None:
                        next_level.add(combined)
                        used.add(left)
                        used.add(right)

        for implicant in current:
            if implicant not in used:
                primes.add(implicant)

        current = sorted(next_level, key=implicant_sort_key)

    return sorted(primes, key=implicant_sort_key)


def implicant_sort_key(implicant: Implicant) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    normalized_values = tuple(2 if value is None else value for value in implicant.values)
    return implicant.literal_count(), normalized_values, tuple(sorted(implicant.covered_indices))


def select_implicants(indices: Iterable[int], n_vars: int) -> list[Implicant]:
    target = sorted(set(indices))
    if not target:
        return []
    target_set = set(target)

    primes = prime_implicants(target, n_vars)
    coverage: dict[int, list[Implicant]] = {index: [] for index in target}
    for implicant in primes:
        for index in implicant.covered_indices:
            if index in coverage:
                coverage[index].append(implicant)

    selected: list[Implicant] = []
    covered: set[int] = set()

    for index in target:
        covering = coverage[index]
        if len(covering) == 1 and covering[0] not in selected:
            selected.append(covering[0])
            covered.update(covering[0].covered_indices & target_set)

    remaining = tuple(index for index in target if index not in covered)
    available = [implicant for implicant in primes if implicant not in selected]
    selected.extend(_optimal_implicant_cover(remaining, available, n_vars))
    return sorted(selected, key=implicant_sort_key)


def _optimal_implicant_cover(
    remaining: tuple[int, ...],
    available: list[Implicant],
    n_vars: int,
) -> list[Implicant]:
    if not remaining:
        return []

    if n_vars <= 4 and len(available) <= 20:
        exact = _exact_implicant_cover(remaining, available)
        if exact is not None:
            return exact

    return _greedy_implicant_cover(remaining, available)


def _exact_implicant_cover(
    remaining: tuple[int, ...],
    available: list[Implicant],
) -> list[Implicant] | None:
    target = set(remaining)

    for size in range(1, len(available) + 1):
        best_subset: tuple[Implicant, ...] | None = None
        best_literal_count: int | None = None
        for subset in combinations(available, size):
            covered = set()
            for implicant in subset:
                covered.update(implicant.covered_indices & target)
            if covered != target:
                continue

            literal_count = sum(implicant.literal_count() for implicant in subset)
            ordered_subset = tuple(sorted(subset, key=implicant_sort_key))
            if (
                best_subset is None
                or literal_count < best_literal_count
                or (
                    literal_count == best_literal_count
                    and tuple(implicant_sort_key(item) for item in ordered_subset)
                    < tuple(implicant_sort_key(item) for item in best_subset)
                )
            ):
                best_subset = ordered_subset
                best_literal_count = literal_count

        if best_subset is not None:
            return list(best_subset)

    return None


def _greedy_implicant_cover(
    remaining: tuple[int, ...],
    available: list[Implicant],
) -> list[Implicant]:
    selected: list[Implicant] = []
    uncovered = list(remaining)
    while remaining:
        best = max(
            available,
            key=lambda implicant: (
                len((implicant.covered_indices & set(uncovered))),
                -implicant.literal_count(),
                sorted(implicant.covered_indices),
            ),
        )
        selected.append(best)
        covered = best.covered_indices & set(uncovered)
        uncovered = [index for index in uncovered if index not in covered]
        available = [implicant for implicant in available if implicant != best]
        remaining = tuple(uncovered)
    return sorted(selected, key=implicant_sort_key)


def implicant_to_sop_term(implicant: Implicant, variable_names: Iterable[str]) -> str:
    pieces = []
    for variable, value in zip(variable_names, implicant.values):
        if value is None:
            continue
        pieces.append(variable if value == 1 else f"{variable}'")
    return "".join(pieces) or "1"


def implicant_to_pos_term(implicant: Implicant, variable_names: Iterable[str]) -> str:
    pieces = []
    for variable, value in zip(variable_names, implicant.values):
        if value is None:
            continue
        pieces.append(variable if value == 0 else f"{variable}'")
    return "(" + " + ".join(pieces) + ")" if pieces else "0"


def simplify_sop(table: TruthTable) -> tuple[str, list[Implicant]]:
    ones = minterms(table)
    if not ones:
        return "0", []
    if len(ones) == 2 ** table.n_vars:
        return "1", [Implicant(tuple(None for _ in range(table.n_vars)), frozenset(ones))]
    implicants = select_implicants(ones, table.n_vars)
    return " + ".join(implicant_to_sop_term(item, table.variable_names) for item in implicants), implicants


def simplify_pos(table: TruthTable) -> tuple[str, list[Implicant]]:
    zeros = maxterms(table)
    if not zeros:
        return "1", []
    if len(zeros) == 2 ** table.n_vars:
        return "0", [Implicant(tuple(None for _ in range(table.n_vars)), frozenset(zeros))]
    implicants = select_implicants(zeros, table.n_vars)
    return " * ".join(implicant_to_pos_term(item, table.variable_names) for item in implicants), implicants


def evaluate_implicant(bits: tuple[int, ...], implicant: Implicant) -> bool:
    for incoming, expected in zip(bits, implicant.values):
        if expected is None:
            continue
        if incoming != expected:
            return False
    return True


def evaluate_sop_expression(bits: tuple[int, ...], implicants: Iterable[Implicant]) -> int:
    return int(any(evaluate_implicant(bits, implicant) for implicant in implicants))


def evaluate_pos_expression(bits: tuple[int, ...], implicants: Iterable[Implicant]) -> int:
    return int(not any(evaluate_implicant(bits, implicant) for implicant in implicants))


def validate_simplified_expression(table: TruthTable, mode: str, implicants: Iterable[Implicant]) -> bool:
    implicant_list = list(implicants)
    for row in table.sorted_rows:
        if mode == "sop":
            observed = evaluate_sop_expression(row.inputs, implicant_list)
        else:
            observed = evaluate_pos_expression(row.inputs, implicant_list)
        if observed != row.output:
            return False
    return True


def format_truth_table(table: TruthTable) -> str:
    rows = table.sorted_rows
    headers = list(table.variable_names) + ["out"]
    widths = [max(len(name), 1) for name in headers]
    for row in rows:
        for index, value in enumerate((*row.inputs, row.output)):
            widths[index] = max(widths[index], len(str(value)))

    line_parts = [" | ".join(header.ljust(widths[index]) for index, header in enumerate(headers))]
    separator = "-+-".join("-" * width for width in widths)
    line_parts.append(separator)
    for row in rows:
        values = (*row.inputs, row.output)
        line_parts.append(" | ".join(str(value).ljust(widths[index]) for index, value in enumerate(values)))
    return "\n".join(line_parts)
