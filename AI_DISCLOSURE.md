# AI Disclosure

AI (Claude, by Anthropic) heavily assisted in writing the Python files in this project (`src/budget_manager/*.py`).

I made all decisions about the project's policies. The AI presented the options and trade-offs, and I chose:

- **Categories:** a small fixed set: food, rent, transport, entertainment, salary, other.
- **Unknown categories:** rejected with a clear error, never mapped to "other" or silently accepted.
- **Currency:** EUR only in Release 1.
- **Whitespace:** leading and trailing spaces are stripped before checking.
- **Capitalization:** normalized (kind and category to lowercase, currency to uppercase).
- **Dates:** strict `YYYY-MM-DD` only.
- **Amounts:** must be a finite number greater than 0 ("inf" and "nan" are rejected).
- **IDs:** must be "T" followed by digits, e.g. T001.

I read through and tested all AI-written code before committing it.
