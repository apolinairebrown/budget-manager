"""File I/O only: load and save transactions as CSV. No business rules here.

Design choices (Release 1):
- Format is CSV, so the data can be opened in a spreadsheet.
- On load, every row is checked; if any rows are invalid, all their errors are
  reported together in one ValidationError and nothing is loaded.
- Row numbers match the line number in the file (the header is line 1),
  so the first data row is "Row 2".
- Duplicate IDs are not checked here; services.py checks them when adding.
- A missing file is an error, not an empty list.
- Amounts are saved with 2 decimals (e.g. 18.50).
"""

import csv
from pathlib import Path

from budget_manager.models import Transaction
from budget_manager.validation import REQUIRED_FIELDS, ValidationError, validate_transaction


def load_transactions(path: str | Path) -> list[Transaction]:
    """Read a CSV file and return its transactions, all validated.

    Raises FileNotFoundError if the file does not exist, and ValidationError
    if the header is wrong or any row is invalid.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        header = reader.fieldnames or []
        missing = [field for field in REQUIRED_FIELDS if field not in header]
        if missing:
            raise ValidationError(f"{path}: missing column(s) {missing} in header.")

        transactions = []
        errors = []
        # The header is line 1, so data rows start at 2.
        for row_number, raw in enumerate(reader, start=2):
            try:
                transactions.append(validate_transaction(raw, row=row_number))
            except ValidationError as error:
                errors.append(str(error))

    if errors:
        summary = f"{path}: {len(errors)} invalid row(s), nothing was loaded:"
        raise ValidationError("\n".join([summary] + ["  " + e for e in errors]))

    return transactions


def save_transactions(path: str | Path, transactions: list[Transaction]) -> None:
    """Write all transactions to a CSV file, replacing its contents."""
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        for t in transactions:
            writer.writerow(
                {
                    "id": t.id,
                    "date": t.date.isoformat(),
                    "kind": t.kind,
                    "category": t.category,
                    "amount": f"{t.amount:.2f}",
                    "currency": t.currency,
                }
            )
