from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from logic_core import (  # noqa: E402
    TruthRow,
    build_truth_table,
    canonical_pos,
    canonical_sop,
    maxterms,
    minterms,
    simplify_pos,
    simplify_sop,
    validate_simplified_expression,
)


class LogicCoreTests(unittest.TestCase):
    def test_two_variable_sop_simplification(self) -> None:
        table = build_truth_table(
            ("A", "B"),
            [
                TruthRow((0, 0), 0),
                TruthRow((0, 1), 1),
                TruthRow((1, 0), 1),
                TruthRow((1, 1), 1),
            ],
        )
        simplified, implicants = simplify_sop(table)
        self.assertEqual(canonical_sop(table), "A'B + AB' + AB")
        self.assertEqual(set(simplified.split(" + ")), {"A", "B"})
        self.assertTrue(validate_simplified_expression(table, "sop", implicants))

    def test_three_variable_wraparound(self) -> None:
        table = build_truth_table(
            ("A", "B", "C"),
            [
                TruthRow((0, 0, 0), 1),
                TruthRow((0, 0, 1), 0),
                TruthRow((0, 1, 0), 1),
                TruthRow((0, 1, 1), 0),
                TruthRow((1, 0, 0), 1),
                TruthRow((1, 0, 1), 0),
                TruthRow((1, 1, 0), 1),
                TruthRow((1, 1, 1), 0),
            ],
        )
        simplified, implicants = simplify_sop(table)
        self.assertEqual(simplified, "C'")
        self.assertTrue(validate_simplified_expression(table, "sop", implicants))

    def test_screenshot_case_truth_table(self) -> None:
        table = build_truth_table(
            ("a", "b", "c"),
            [
                TruthRow((0, 0, 0), 0),
                TruthRow((0, 0, 1), 1),
                TruthRow((0, 1, 0), 1),
                TruthRow((0, 1, 1), 1),
                TruthRow((1, 0, 0), 0),
                TruthRow((1, 0, 1), 1),
                TruthRow((1, 1, 0), 1),
                TruthRow((1, 1, 1), 1),
            ],
        )
        simplified, implicants = simplify_sop(table)
        self.assertEqual(minterms(table), [1, 2, 3, 5, 6, 7])
        self.assertEqual(canonical_sop(table), "a'b'c + a'bc' + a'bc + ab'c + abc' + abc")
        self.assertEqual(set(simplified.split(" + ")), {"b", "c"})
        self.assertTrue(validate_simplified_expression(table, "sop", implicants))

    def test_four_variable_case(self) -> None:
        table = build_truth_table(
            ("A", "B", "C", "D"),
            [
                TruthRow((0, 0, 0, 0), 1),
                TruthRow((0, 0, 0, 1), 1),
                TruthRow((0, 0, 1, 0), 0),
                TruthRow((0, 0, 1, 1), 0),
                TruthRow((0, 1, 0, 0), 1),
                TruthRow((0, 1, 0, 1), 1),
                TruthRow((0, 1, 1, 0), 0),
                TruthRow((0, 1, 1, 1), 0),
                TruthRow((1, 0, 0, 0), 1),
                TruthRow((1, 0, 0, 1), 1),
                TruthRow((1, 0, 1, 0), 0),
                TruthRow((1, 0, 1, 1), 0),
                TruthRow((1, 1, 0, 0), 1),
                TruthRow((1, 1, 0, 1), 1),
                TruthRow((1, 1, 1, 0), 0),
                TruthRow((1, 1, 1, 1), 0),
            ],
        )
        simplified, implicants = simplify_sop(table)
        self.assertEqual(simplified, "C'")
        self.assertTrue(validate_simplified_expression(table, "sop", implicants))

    def test_valid_pos_case(self) -> None:
        table = build_truth_table(
            ("A", "B", "C"),
            [
                TruthRow((0, 0, 0), 0),
                TruthRow((0, 0, 1), 0),
                TruthRow((0, 1, 0), 0),
                TruthRow((0, 1, 1), 1),
                TruthRow((1, 0, 0), 0),
                TruthRow((1, 0, 1), 0),
                TruthRow((1, 1, 0), 0),
                TruthRow((1, 1, 1), 1),
            ],
        )
        simplified, implicants = simplify_pos(table)
        self.assertEqual(canonical_pos(table), "(A + B + C) * (A + B + C') * (A + B' + C) * (A' + B + C) * (A' + B + C') * (A' + B' + C)")
        self.assertEqual(maxterms(table), [0, 1, 2, 4, 5, 6])
        self.assertEqual(simplified, "(B) * (C)")
        self.assertTrue(validate_simplified_expression(table, "pos", implicants))

    def test_four_variable_sop_uses_minimal_cover(self) -> None:
        rows = []
        for index in range(16):
            bits = tuple((index >> shift) & 1 for shift in range(3, -1, -1))
            output = 1 if index in {0, 1, 3, 4, 6, 7, 8, 9} else 0
            rows.append(TruthRow(bits, output))

        table = build_truth_table(("A", "B", "C", "D"), rows)
        simplified, implicants = simplify_sop(table)

        self.assertEqual(simplified, "B'C' + A'BD' + A'CD")
        self.assertEqual(len(implicants), 3)
        self.assertTrue(validate_simplified_expression(table, "sop", implicants))

    def test_all_zero_function(self) -> None:
        table = build_truth_table(
            ("A", "B"),
            [
                TruthRow((0, 0), 0),
                TruthRow((0, 1), 0),
                TruthRow((1, 0), 0),
                TruthRow((1, 1), 0),
            ],
        )
        simplified, implicants = simplify_sop(table)
        self.assertEqual(minterms(table), [])
        self.assertEqual(simplified, "0")
        self.assertTrue(validate_simplified_expression(table, "sop", implicants))

    def test_all_one_function(self) -> None:
        table = build_truth_table(
            ("A", "B"),
            [
                TruthRow((0, 0), 1),
                TruthRow((0, 1), 1),
                TruthRow((1, 0), 1),
                TruthRow((1, 1), 1),
            ],
        )
        simplified, implicants = simplify_pos(table)
        self.assertEqual(maxterms(table), [])
        self.assertEqual(simplified, "1")
        self.assertTrue(validate_simplified_expression(table, "pos", implicants))

    def test_invalid_row_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly 4 rows"):
            build_truth_table(
                ("A", "B"),
                [
                    TruthRow((0, 0), 0),
                    TruthRow((0, 1), 1),
                    TruthRow((1, 0), 1),
                ],
            )

    def test_duplicate_input_combination(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate input combination"):
            build_truth_table(
                ("A", "B"),
                [
                    TruthRow((0, 0), 0),
                    TruthRow((0, 0), 1),
                    TruthRow((1, 0), 1),
                    TruthRow((1, 1), 0),
                ],
            )

    def test_rejects_less_than_two_variables(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 2"):
            build_truth_table(
                ("A",),
                [
                    TruthRow((0,), 0),
                    TruthRow((1,), 1),
                ],
            )

    def test_n_greater_than_four_keeps_canonical_generation(self) -> None:
        rows = []
        for value in range(32):
            bits = tuple((value >> shift) & 1 for shift in range(4, -1, -1))
            rows.append(TruthRow(bits, int(sum(bits) >= 3)))
        table = build_truth_table(("A", "B", "C", "D", "E"), rows)
        canonical = canonical_sop(table)
        self.assertIn("A'B'CDE", canonical)
        simplified, implicants = simplify_sop(table)
        self.assertTrue(validate_simplified_expression(table, "sop", implicants))


class CliTests(unittest.TestCase):
    def test_cli_output_sections(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "task2.py"),
                "--vars",
                "3",
                "--mode",
                "sop",
                "--input",
                str(PROJECT_ROOT / "samples" / "three_var_sop.csv"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Truth table", result.stdout)
        self.assertIn("Canonical equation (SOP)", result.stdout)
        self.assertIn("Minterm / Maxterm list", result.stdout)
        self.assertIn("K-Map grouping", result.stdout)
        self.assertIn("Simplified Boolean expression", result.stdout)
        self.assertIn("Validation result\nPASS", result.stdout)

    def test_cli_rejects_invalid_output_value(self) -> None:
        invalid_csv = PROJECT_ROOT / "tests" / "invalid_output.csv"
        invalid_csv.write_text("A,B,out\n0,0,0\n0,1,2\n1,0,1\n1,1,0\n", encoding="utf-8")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "task2.py"),
                    "--vars",
                    "2",
                    "--input",
                    str(invalid_csv),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be 0 or 1", result.stderr)
        finally:
            invalid_csv.unlink(missing_ok=True)

    def test_interactive_names_strip_commas(self) -> None:
        from task2 import interactive_truth_table, render_report

        answers = iter(
            [
                "2",
                "a, b",
                "0,0,1",
                "0,1,0",
                "1,0,0",
                "1,1,1",
            ]
        )
        with patch("builtins.input", side_effect=lambda _: next(answers)):
            table = interactive_truth_table(None, "sop")

        report = render_report(table, "sop")
        self.assertIn("a'b' + ab", report)
        self.assertNotIn("a,'", report)

    def test_cli_reports_missing_input_file_cleanly(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "task2.py"),
                "--vars",
                "3",
                "--input",
                str(PROJECT_ROOT / "missing.csv"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
