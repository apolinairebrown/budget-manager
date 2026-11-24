"""Tests for the budget manager. Run from the project root with:

    python -m unittest discover -s tests -v

Every test states its expected output explicitly.
"""

import contextlib
import datetime
import io
import sys
import tempfile
import unittest
from pathlib import Path

# Make the package in src/ importable without installing it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from budget_manager import cli, services, storage  # noqa: E402
from budget_manager.models import Transaction  # noqa: E402
from budget_manager.validation import ValidationError, validate_transaction  # noqa: E402


def make_raw(**overrides) -> dict:
    """A valid raw row (all text, like a CSV line). Override fields to break it."""
    raw = {
        "id": "T001",
        "date": "2026-09-04",
        "kind": "expense",
        "category": "food",
        "amount": "18.50",
        "currency": "EUR",
    }
    raw.update(overrides)
    return raw


class RequiredTests(unittest.TestCase):
    """The three tests the brief requires: one normal case, two boundary cases."""

    def test_normal_summary_balance(self):
        # Expected: 1000.00 income - 18.50 expense = 981.50 balance.
        transactions = []
        transactions = services.add_transaction(
            transactions, validate_transaction(make_raw(id="T001", amount="18.50"))
        )
        transactions = services.add_transaction(
            transactions,
            validate_transaction(make_raw(id="T002", kind="income", category="salary", amount="1000")),
        )
        summary = services.summarize(transactions)
        self.assertEqual(summary["income"], 1000.00)
        self.assertEqual(summary["expenses"], 18.50)
        self.assertEqual(summary["balance"], 981.50)

    def test_amount_zero_or_negative_is_rejected(self):
        # Expected: ValidationError "Row 4: amount must be > 0." for -5 and for 0.
        for bad_amount in ["-5", "0"]:
            with self.subTest(amount=bad_amount):
                with self.assertRaises(ValidationError) as caught:
                    validate_transaction(make_raw(amount=bad_amount), row=4)
                self.assertEqual(str(caught.exception), "Row 4: amount must be > 0.")

    def test_save_then_load_round_trips_exactly(self):
        # Expected: the loaded list is identical to the saved list.
        original = [
            Transaction("T001", datetime.date(2026, 9, 1), "income", "salary", 1000.0, "EUR"),
            Transaction("T002", datetime.date(2026, 9, 4), "expense", "food", 18.5, "EUR"),
            Transaction("T003", datetime.date(2026, 9, 5), "expense", "transport", 0.1, "EUR"),
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "transactions.csv"
            storage.save_transactions(path, original)
            self.assertEqual(storage.load_transactions(path), original)


class DesignDecisionTests(unittest.TestCase):
    """One test per key design decision (see DESIGN.md and AI_DISCLOSURE.md)."""

    def test_unknown_category_is_rejected(self):
        # Expected: rejected, never mapped to "other".
        with self.assertRaises(ValidationError) as caught:
            validate_transaction(make_raw(category="pizza"), row=4)
        self.assertIn("Row 4: unknown category 'pizza'", str(caught.exception))

    def test_compact_date_is_rejected(self):
        # Expected: "20260904" is rejected even though Python 3.11+ can parse it.
        with self.assertRaises(ValidationError) as caught:
            validate_transaction(make_raw(date="20260904"))
        self.assertEqual(
            str(caught.exception), "date must be in YYYY-MM-DD format, got '20260904'."
        )

    def test_impossible_date_is_rejected(self):
        # Expected: month 13 is not a real calendar date.
        with self.assertRaises(ValidationError) as caught:
            validate_transaction(make_raw(date="2026-13-40"))
        self.assertEqual(str(caught.exception), "date '2026-13-40' is not a real calendar date.")

    def test_more_than_two_decimals_is_rejected(self):
        # Expected: rejected instead of silently rounded to 18.56 on save.
        with self.assertRaises(ValidationError) as caught:
            validate_transaction(make_raw(amount="18.555"))
        self.assertEqual(
            str(caught.exception), "amount must have at most 2 decimals, got '18.555'."
        )

    def test_spaces_and_case_are_normalized(self):
        # Expected: " Food " -> "food", " Expense " -> "expense", "eur" -> "EUR".
        t = validate_transaction(make_raw(kind=" Expense ", category=" Food ", currency="eur"))
        self.assertEqual((t.kind, t.category, t.currency), ("expense", "food", "EUR"))

    def test_duplicate_id_is_rejected(self):
        # Expected: adding T001 twice raises, and the original list is unchanged.
        first = validate_transaction(make_raw(id="T001"))
        transactions = services.add_transaction([], first)
        with self.assertRaises(ValidationError) as caught:
            services.add_transaction(transactions, validate_transaction(make_raw(id="T001")))
        self.assertEqual(str(caught.exception), "id 'T001' already exists.")
        self.assertEqual(transactions, [first])

    def test_load_reports_every_bad_row_and_loads_nothing(self):
        # Expected: one error listing rows 3, 4 and 5 (file line numbers).
        content = (
            "id,date,kind,category,amount,currency\n"
            "T001,2026-09-04,expense,food,18.50,EUR\n"
            "T002,2026-13-40,expense,food,5.00,EUR\n"
            "T003,2026-09-04,expense,pizza,5.00,EUR\n"
            "T004,2026-09-04,expense,food,-1,EUR\n"
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValidationError) as caught:
                storage.load_transactions(path)
        message = str(caught.exception)
        self.assertIn("3 invalid row(s), nothing was loaded", message)
        self.assertIn("Row 3: date '2026-13-40' is not a real calendar date.", message)
        self.assertIn("Row 4: unknown category 'pizza'", message)
        self.assertIn("Row 5: amount must be > 0.", message)

    def test_cli_prints_error_instead_of_crashing(self):
        # Expected: exit code 1, a clear message on stderr, and the file unchanged.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "transactions.csv"
            storage.save_transactions(path, [])
            before = path.read_text(encoding="utf-8")

            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                exit_code = cli.main(
                    ["--file", str(path), "add", "--kind", "expense",
                     "--category", "food", "--amount", "-5"]
                )

            self.assertEqual(exit_code, 1)
            self.assertEqual(errors.getvalue().strip(), "Error: amount must be > 0.")
            self.assertEqual(path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
