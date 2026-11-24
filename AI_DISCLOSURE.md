# AI Disclosure

AI (Claude, by Anthropic) heavily assisted in writing the Python files in this project (`src/budget_manager/*.py`).

I made all decisions about the project's policies. The AI presented the options and trade-offs, and I chose:

- **Categories:** a small fixed set: food, rent, transport, entertainment, salary, other.
- **Unknown categories:** rejected with a clear error, never mapped to "other" or silently accepted.
- **Currency:** EUR only in Release 1.
- **Whitespace:** leading and trailing spaces are stripped before checking.
- **Capitalization:** normalized (kind and category to lowercase, currency to uppercase).
- **Dates:** strict `YYYY-MM-DD` only.
- **Amounts:** must be a finite number greater than 0 ("inf" and "nan" are rejected), with at most 2 decimals (rejected rather than rounded, so no data is silently changed).
- **IDs:** must be "T" followed by digits, e.g. T001.
- **File format:** CSV.
- **Invalid rows on load:** every row is checked, all errors are reported together, and nothing is loaded.
- **Row numbers in errors:** match the line number in the file (the header is line 1).
- **Duplicate IDs:** checked in the service layer when adding, not on load.
- **Missing data file:** an error, not an empty list.
- **Saved amounts:** written with 2 decimals (e.g. 18.50).
- **Adding:** returns a new list instead of changing the existing one.
- **IDs when adding:** always auto-generated (highest number + 1).
- **List order:** sorted by date (oldest first), then by id.
- **Filters:** normalized and checked with the same rules as validation (unknown values give an error).
- **Summary:** total income, total expenses, balance and per-category totals, rounded to 2 decimals.
- **Duplicate ID error:** reuses ValidationError.
- **How to run:** a small launcher in the project root (`python budget.py ...`).
- **Data file:** `data/transactions.csv` by default (`--file` to choose another), keeping the sample data untouched.
- **Adding:** date defaults to today, currency defaults to EUR.
- **List output:** an aligned table.
- **Python version:** requires Python 3.10+ (no backport to 3.9).

I read through and tested all AI-written code before committing it.
