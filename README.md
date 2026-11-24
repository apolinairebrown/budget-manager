# Budget Manager (Release 1)

A command-line personal budget manager: add, list and summarize income and expenses, saved to a CSV file. Every input is validated, and invalid data is rejected with a clear message instead of being silently fixed.

## Setup

- **Requires Python 3.10+.** No packages to install (standard library only).

```bash
git clone https://github.com/apolinairebrown/budget-manager.git
cd budget-manager
python --version        # must be 3.10 or newer (use python3 if python is not found)
```

## Run

All commands run from the project root:

```bash
python budget.py add --kind expense --category food --amount 9.80 [--date YYYY-MM-DD] [--currency EUR]
python budget.py list [--kind expense|income] [--category food]
python budget.py summary
```

- Data is stored in `data/transactions.csv`. Use `--file PATH` (before the command) to use another file.
- `add` generates the ID automatically. The date defaults to today and the currency to EUR.
- Categories: `food`, `rent`, `transport`, `entertainment`, `salary`, `other`.

## Example

```text
$ python budget.py --file data/sample_transactions.csv summary
Income:        1500.00 EUR
Expenses:       748.79 EUR
Balance:        751.21 EUR

By category:
  entertainment       12.99
  food                60.80
  rent               650.00
  salary            1500.00
  transport           25.00

$ python budget.py add --kind expense --category pizza --amount 5
Error: unknown category 'pizza'. Allowed: ['entertainment', 'food', 'other', 'rent', 'salary', 'transport'].

$ python budget.py --file data/invalid_transactions.csv list
Error: data/invalid_transactions.csv: 10 invalid row(s), nothing was loaded:
  Row 3: amount must be > 0.
  Row 5: amount must have at most 2 decimals, got '18.555'.
  Row 6: date '2026-13-40' is not a real calendar date.
  Row 8: unknown category 'pizza'. ...
  (one row per validation rule)
```

## Test

```bash
python -m unittest discover -s tests -v
```

Runs 11 tests: the three required ones (normal balance of 981.50, amount ≤ 0 rejected, save/load round trip) plus one per key validation rule.

## Project layout

```text
budget.py                  launcher (adds src/ to the import path)
src/budget_manager/
  models.py                Transaction dataclass and allowed values
  validation.py            all input rules and error messages
  services.py              business logic: add, list, summarize (no I/O)
  storage.py               load/save CSV
  cli.py                   command-line arguments and printing
tests/test_budget.py       unit tests
data/                      transactions.csv (default), sample and invalid examples
```

## Known limitations

- Only EUR is supported, so summaries never mix currencies.
- Amounts are stored as floats and totals are rounded to 2 decimals. Release 2 could use `Decimal`.
- No edit, delete or undo.
- CSV storage only, and the whole file is rewritten on every save.
- Duplicate IDs in a hand-edited CSV file are not detected on load (they are rejected when adding through the CLI).
