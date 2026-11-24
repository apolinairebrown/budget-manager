from dataclasses import dataclass
import datetime

ALLOWED_KINDS = {"expense", "income"}

# Policy: unknown categories are rejected with a ValidationError in
# validation.py. They are never mapped to "other" or silently accepted.
ALLOWED_CATEGORIES = {"food", "rent", "transport", "entertainment", "salary", "other"}

# Release 1 supports a single currency, so summaries never mix currencies.
ALLOWED_CURRENCIES = {"EUR"}


@dataclass
class Transaction:
    id: str
    date: datetime.date
    kind: str
    category: str
    amount: float
    currency: str
