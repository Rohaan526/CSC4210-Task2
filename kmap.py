from __future__ import annotations

from dataclasses import dataclass

from logic_core import Implicant, TruthTable, inputs_to_index


GRAY_CODES: dict[int, list[tuple[int, ...]]] = {
    1: [(0,), (1,)],
    2: [(0, 0), (0, 1), (1, 1), (1, 0)],
}


@dataclass(frozen=True)
class KMapCell:
    row_bits: tuple[int, ...]
    column_bits: tuple[int, ...]
    index: int
    output: int


def split_dimensions(n_vars: int) -> tuple[int, int]:
    if n_vars == 2:
        return 1, 1
    if n_vars == 3:
        return 1, 2
    if n_vars == 4:
        return 2, 2
    raise ValueError("K-map rendering is supported only for 2 to 4 variables.")


def build_kmap(table: TruthTable) -> list[list[KMapCell]]:
    row_vars, col_vars = split_dimensions(table.n_vars)
    row_codes = GRAY_CODES[row_vars]
    col_codes = GRAY_CODES[col_vars]
    outputs = {row.inputs: row.output for row in table.sorted_rows}

    grid: list[list[KMapCell]] = []
    for row_bits in row_codes:
        current_row: list[KMapCell] = []
        for col_bits in col_codes:
            bits = row_bits + col_bits
            current_row.append(
                KMapCell(
                    row_bits=row_bits,
                    column_bits=col_bits,
                    index=inputs_to_index(bits),
                    output=outputs[bits],
                )
            )
        grid.append(current_row)
    return grid


def format_kmap(table: TruthTable) -> str:
    grid = build_kmap(table)
    row_vars, col_vars = split_dimensions(table.n_vars)
    row_label = "".join(table.variable_names[:row_vars])
    col_label = "".join(table.variable_names[row_vars:])

    header = f"{row_label}\\{col_label}".strip("\\")
    col_headers = ["".join(str(bit) for bit in cell.column_bits) for cell in grid[0]]
    widths = [max(len(header), 2)] + [max(len(name), 5) for name in col_headers]

    lines = []
    first_row = [header.ljust(widths[0])]
    for index, name in enumerate(col_headers, start=1):
        first_row.append(name.center(widths[index]))
    lines.append(" | ".join(first_row))
    lines.append("-+-".join("-" * width for width in widths))

    for row in grid:
        row_name = "".join(str(bit) for bit in row[0].row_bits)
        parts = [row_name.ljust(widths[0])]
        for index, cell in enumerate(row, start=1):
            parts.append(f"{cell.output} m{cell.index}".center(widths[index]))
        lines.append(" | ".join(parts))

    return "\n".join(lines)


def format_groupings(implicants: list[Implicant], table: TruthTable, mode: str) -> str:
    if table.n_vars > 4:
        return "K-map simplification skipped because the assignment limits K-map work to 2-4 variables."
    if not implicants:
        return "No K-map groups are needed for this function."

    lines = []
    for index, implicant in enumerate(implicants, start=1):
        covered = ", ".join(str(value) for value in sorted(implicant.covered_indices))
        if mode == "sop":
            term = _implicant_label_sop(implicant, table.variable_names)
        else:
            term = _implicant_label_pos(implicant, table.variable_names)
        lines.append(f"Group {index}: cells {{{covered}}} -> {term}")
    return "\n".join(lines)


def _implicant_label_sop(implicant: Implicant, variable_names: tuple[str, ...]) -> str:
    pieces = []
    for variable, value in zip(variable_names, implicant.values):
        if value is None:
            continue
        pieces.append(variable if value == 1 else f"{variable}'")
    return "".join(pieces) or "1"


def _implicant_label_pos(implicant: Implicant, variable_names: tuple[str, ...]) -> str:
    pieces = []
    for variable, value in zip(variable_names, implicant.values):
        if value is None:
            continue
        pieces.append(variable if value == 0 else f"{variable}'")
    return "(" + " + ".join(pieces) + ")" if pieces else "0"
