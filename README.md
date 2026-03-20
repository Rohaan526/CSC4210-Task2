# Process Design Task 2

Author: Rohaan Mohammed

This project solves Georgia State University CSC 4210/6210 Processor Design Semester Project Task 2: converting a truth table into a canonical Boolean equation, simplifying it with Karnaugh-map grouping for 2-4 variables, and validating the simplified result against the original truth table.

## Requirements

- Python 3.10 or newer
- No third-party packages are required

## Project Files

- `task2.py`: command-line entrypoint
- `logic_core.py`: truth-table validation, canonical SOP/POS generation, simplification helpers, and validation
- `kmap.py`: K-map layout and grouping output for 2-4 variables
- `samples/`: example truth tables for demos
- `test_task2.py`: automated tests

## Input Format

CSV input must:
- include one column per input variable followed by `out`
- use only `0` and `1`
- include exactly `2^n` rows
- include each input combination exactly once

Example:

```csv
A,B,C,out
0,0,0,0
0,0,1,1
0,1,0,1
0,1,1,1
1,0,0,0
1,0,1,1
1,1,0,1
1,1,1,1
```

## Usage

Run with a CSV file:

```bash
python3 task2.py --vars 3 --mode sop --input samples/three_var_sop.csv
python3 task2.py --vars 3 --mode pos --input samples/three_var_pos.csv
python3 task2.py --vars 4 --mode sop --input samples/four_var_wraparound.csv
python3 task2.py --vars 3 --mode sop --input samples/screenshot_case.csv
```

Run interactively:

```bash
python3 task2.py --interactive
```

## Program Output

The program prints the assignment-required sections in this order:

1. Truth table
2. Canonical equation (SOP or POS)
3. Minterm / Maxterm list
4. K-Map
5. K-Map grouping
6. Simplified Boolean expression
7. Validation result (`PASS` or `FAIL`)

For `n > 4`, the program still validates the truth table and generates canonical equations, but K-map rendering and K-map grouping are skipped because the assignment limits K-map work to 2-4 variables.

## Testing

Run the automated tests from this directory:

```bash
python3 -m unittest discover -s tests -v
```
