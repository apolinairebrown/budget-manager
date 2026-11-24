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

I read through and tested all AI-written code before committing it.
