"""All input checks live here, so the CLI and the CSV loader share the same rules.

Design choices (Release 1):
- Leading/trailing spaces are stripped before checking.
- Case is normalized: kind and category are lowercased, currency is uppercased.
- Dates must be exactly YYYY-MM-DD (the compact form "20260904" is rejected).
- Amounts must be finite numbers > 0 ("inf" and "nan" are rejected) with at most
  2 decimals, so saving and loading never changes an amount.
- IDs must be "T" followed by digits, e.g. T001.
- Duplicate IDs are checked in services.py, because this function sees one row at a time.
"""

import datetime
import math
import re

from budget_manager.models import (
    ALLOWED_CATEGORIES,
    ALLOWED_CURRENCIES,
    ALLOWED_KINDS,
    Transaction,
)

REQUIRED_FIELDS = ["id", "date", "kind", "category", "amount", "currency"]

ID_PATTERN = re.compile(r"T\d+")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


class ValidationError(ValueError):
    """Raised when input data breaks a rule. The message is meant for the user."""


def validate_transaction(raw: dict, row: int | None = None) -> Transaction:
    """Check one raw record (all values as text) and return a Transaction.

    Raises ValidationError with an actionable message on the first problem found.
    If row is given, the message starts with "Row <n>: ".
    """
    prefix = f"Row {row}: " if row is not None else ""

    def fail(message: str) -> None:
        raise ValidationError(prefix + message)

    # 1. Every field present and not blank. Strip spaces from each value.
    clean = {}
    for field in REQUIRED_FIELDS:
        value = raw.get(field)
        if value is None or str(value).strip() == "":
            fail(f"missing required field '{field}'.")
        clean[field] = str(value).strip()

    # 2. id: "T" followed by digits.
    if not ID_PATTERN.fullmatch(clean["id"]):
        fail(f"id must look like T001, got '{clean['id']}'.")

    # 3. date: strict YYYY-MM-DD, and a real calendar date.
    if not DATE_PATTERN.fullmatch(clean["date"]):
        fail(f"date must be in YYYY-MM-DD format, got '{clean['date']}'.")
    try:
        date = datetime.date.fromisoformat(clean["date"])
    except ValueError:
        fail(f"date '{clean['date']}' is not a real calendar date.")

    # 4. kind: normalized to lowercase, must be allowed.
    kind = clean["kind"].lower()
    if kind not in ALLOWED_KINDS:
        fail(f"kind must be one of {sorted(ALLOWED_KINDS)}, got '{clean['kind']}'.")

    # 5. category: normalized to lowercase, unknown categories are rejected.
    category = clean["category"].lower()
    if category not in ALLOWED_CATEGORIES:
        fail(
            f"unknown category '{clean['category']}'. "
            f"Allowed: {sorted(ALLOWED_CATEGORIES)}."
        )

    # 6. amount: a finite number greater than 0.
    try:
        amount = float(clean["amount"])
    except ValueError:
        fail(f"amount must be a number, got '{clean['amount']}'.")
    if not math.isfinite(amount):
        fail(f"amount must be a finite number, got '{clean['amount']}'.")
    if amount <= 0:
        fail("amount must be > 0.")
    if round(amount, 2) != amount:
        fail(f"amount must have at most 2 decimals, got '{clean['amount']}'.")

    # 7. currency: normalized to uppercase, must be allowed.
    currency = clean["currency"].upper()
    if currency not in ALLOWED_CURRENCIES:
        fail(
            f"currency must be one of {sorted(ALLOWED_CURRENCIES)}, "
            f"got '{clean['currency']}'."
        )

    return Transaction(
        id=clean["id"],
        date=date,
        kind=kind,
        category=category,
        amount=amount,
        currency=currency,
    )
