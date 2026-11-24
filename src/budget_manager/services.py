"""Business logic only: no input(), no print(), no file access.

Design choices (Release 1):
- add_transaction returns a new list and never changes the one passed in.
- Duplicate IDs are rejected here with a ValidationError.
- IDs are auto-generated: highest existing number + 1 (T001, T002, ...).
- list_transactions sorts by date (oldest first), then by id.
- Filter values are normalized and checked with the same rules as validation.
- All summary totals are rounded to 2 decimals.
"""

from budget_manager.models import Transaction
from budget_manager.validation import ValidationError, validate_filters


def add_transaction(transactions: list[Transaction], new: Transaction) -> list[Transaction]:
    """Return a new list with `new` added. Raises ValidationError on a duplicate id."""
    for t in transactions:
        if t.id == new.id:
            raise ValidationError(f"id '{new.id}' already exists.")
    return transactions + [new]


def next_id(transactions: list[Transaction]) -> str:
    """Return the next free id: one more than the highest existing number."""
    highest = max((int(t.id[1:]) for t in transactions), default=0)
    return f"T{highest + 1:03d}"


def list_transactions(
    transactions: list[Transaction],
    kind: str | None = None,
    category: str | None = None,
) -> list[Transaction]:
    """Return matching transactions, sorted by date then id.

    Raises ValidationError if a filter value is not allowed.
    """
    kind, category = validate_filters(kind, category)
    result = [
        t
        for t in transactions
        if (kind is None or t.kind == kind)
        and (category is None or t.category == category)
    ]
    return sorted(result, key=lambda t: (t.date, t.id))


def summarize(transactions: list[Transaction]) -> dict:
    """Return total income, total expenses, balance and totals per category."""
    income = sum(t.amount for t in transactions if t.kind == "income")
    expenses = sum(t.amount for t in transactions if t.kind == "expense")

    by_category: dict[str, float] = {}
    for t in transactions:
        by_category[t.category] = by_category.get(t.category, 0) + t.amount

    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "balance": round(income - expenses, 2),
        "by_category": {cat: round(total, 2) for cat, total in sorted(by_category.items())},
    }
