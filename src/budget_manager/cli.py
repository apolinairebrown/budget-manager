"""Command-line interface: argument parsing and printing only.

Every command follows the same pattern:
    load (storage) -> do the work (services) -> save if changed (storage) -> print

Design choices (Release 1):
- Default data file is data/transactions.csv; --file chooses another.
- add: id is auto-generated, --date defaults to today, --currency defaults to EUR.
- Errors are printed as one clear message (no traceback) and exit with code 1.
"""

import argparse
import datetime
import sys
from pathlib import Path

from budget_manager import services, storage
from budget_manager.validation import ValidationError, validate_transaction

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FILE = PROJECT_ROOT / "data" / "transactions.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="budget.py", description="Personal budget manager (Release 1)."
    )
    parser.add_argument(
        "--file", default=str(DEFAULT_FILE), help="CSV data file (default: data/transactions.csv)"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="add a transaction")
    add.add_argument("--kind", required=True, help="expense or income")
    add.add_argument("--category", required=True, help="e.g. food, rent, salary")
    add.add_argument("--amount", required=True, help="positive number, max 2 decimals")
    add.add_argument("--date", default=None, help="YYYY-MM-DD (default: today)")
    add.add_argument("--currency", default="EUR", help="currency code (default: EUR)")

    list_cmd = commands.add_parser("list", help="list transactions")
    list_cmd.add_argument("--kind", default=None, help="only this kind")
    list_cmd.add_argument("--category", default=None, help="only this category")

    commands.add_parser("summary", help="show totals and balance")

    return parser


def cmd_add(args) -> None:
    transactions = storage.load_transactions(args.file)
    raw = {
        "id": services.next_id(transactions),
        "date": args.date or datetime.date.today().isoformat(),
        "kind": args.kind,
        "category": args.category,
        "amount": args.amount,
        "currency": args.currency,
    }
    new = validate_transaction(raw)
    transactions = services.add_transaction(transactions, new)
    storage.save_transactions(args.file, transactions)
    print(
        f"Added {new.id}: {new.date.isoformat()} {new.kind} {new.category} "
        f"{new.amount:.2f} {new.currency}"
    )


def cmd_list(args) -> None:
    transactions = storage.load_transactions(args.file)
    rows = services.list_transactions(transactions, kind=args.kind, category=args.category)
    if not rows:
        print("No transactions found.")
        return
    print(f"{'ID':<6}{'DATE':<12}{'KIND':<9}{'CATEGORY':<15}{'AMOUNT':>10} CUR")
    for t in rows:
        print(
            f"{t.id:<6}{t.date.isoformat():<12}{t.kind:<9}{t.category:<15}"
            f"{t.amount:>10.2f} {t.currency}"
        )


def cmd_summary(args) -> None:
    transactions = storage.load_transactions(args.file)
    summary = services.summarize(transactions)
    print(f"{'Income:':<12}{summary['income']:>10.2f} EUR")
    print(f"{'Expenses:':<12}{summary['expenses']:>10.2f} EUR")
    print(f"{'Balance:':<12}{summary['balance']:>10.2f} EUR")
    if summary["by_category"]:
        print("\nBy category:")
        for category, total in summary["by_category"].items():
            print(f"  {category:<15}{total:>10.2f}")


COMMANDS = {"add": cmd_add, "list": cmd_list, "summary": cmd_summary}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        COMMANDS[args.command](args)
    except (ValidationError, FileNotFoundError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
