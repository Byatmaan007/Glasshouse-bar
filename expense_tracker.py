"""Simple CLI for tracking restaurant income and expenses.

Data is stored in a JSON file next to this script by default. Use the
`--data-file` flag to point to another location (useful for testing or if
running multiple ledgers).
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Iterable, List, Literal, Tuple

TransactionType = Literal["income", "expense"]


@dataclass
class Transaction:
    kind: TransactionType
    amount: float
    category: str
    description: str
    date: str  # ISO formatted (YYYY-MM-DD)

    def normalized(self) -> "Transaction":
        return Transaction(
            kind=self.kind,
            amount=round(self.amount, 2),
            category=self.category.strip() or "uncategorized",
            description=self.description.strip(),
            date=self.date,
        )


DEFAULT_DATA_FILE = Path(__file__).resolve().with_name("expenses.json")


def _load_transactions(data_file: Path) -> List[Transaction]:
    if not data_file.exists():
        return []
    with data_file.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Transaction(**item) for item in raw]


def _save_transactions(data_file: Path, transactions: Iterable[Transaction]) -> None:
    payload = [asdict(t.normalized()) for t in transactions]
    data_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _validate_date(value: str | None) -> str:
    if value is None:
        return date.today().isoformat()
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Dates must be in ISO format (YYYY-MM-DD)") from exc


def add_transaction(
    *,
    kind: TransactionType,
    amount: float,
    category: str,
    description: str,
    date_str: str | None = None,
    data_file: Path = DEFAULT_DATA_FILE,
) -> Transaction:
    if amount <= 0:
        raise ValueError("Amount must be positive")

    normalized_kind: TransactionType = kind
    iso_date = _validate_date(date_str)

    transaction = Transaction(
        kind=normalized_kind,
        amount=amount,
        category=category,
        description=description,
        date=iso_date,
    ).normalized()

    transactions = _load_transactions(data_file)
    transactions.append(transaction)
    _save_transactions(data_file, transactions)
    return transaction


def summarize(transactions: Iterable[Transaction]) -> Tuple[float, float, float, dict[str, float]]:
    income_total = 0.0
    expense_total = 0.0
    category_totals: dict[str, float] = {}

    for txn in transactions:
        if txn.kind == "income":
            income_total += txn.amount
            category_totals[txn.category] = category_totals.get(txn.category, 0) + txn.amount
        else:
            expense_total += txn.amount
            category_totals[txn.category] = category_totals.get(txn.category, 0) - txn.amount

    net = income_total - expense_total
    return income_total, expense_total, net, category_totals


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def _print_transactions(transactions: Iterable[Transaction]) -> None:
    header = f"{'Date':<12} {'Type':<8} {'Category':<18} {'Amount':>12}  Description"
    print(header)
    print("-" * len(header))
    for txn in transactions:
        sign = 1 if txn.kind == "income" else -1
        amount = sign * txn.amount
        print(
            f"{txn.date:<12} {txn.kind:<8} {txn.category:<18} {amount:>12.2f}  {txn.description}"
        )


def _print_summary(transactions: List[Transaction]) -> None:
    income_total, expense_total, net, categories = summarize(transactions)
    print("Totals:")
    print(f"  Income:  {_format_currency(income_total)}")
    print(f"  Expense: {_format_currency(expense_total)}")
    print(f"  Net:     {_format_currency(net)}")

    if categories:
        print("\nBy category (income positive, expense negative):")
        for category, total in sorted(categories.items()):
            print(f"  {category:<18} {_format_currency(total)}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track restaurant income and expenses")
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="Location of the ledger JSON file (default: expenses.json next to this script)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Record an income or expense")
    add_parser.add_argument("kind", choices=["income", "expense"], help="Type of transaction")
    add_parser.add_argument("amount", type=float, help="Transaction amount (positive number)")
    add_parser.add_argument("description", help="Short description")
    add_parser.add_argument(
        "--category",
        default="uncategorized",
        help="Category label (e.g., food, supplies, payroll)",
    )
    add_parser.add_argument(
        "--date",
        dest="date_str",
        help="Transaction date in YYYY-MM-DD (defaults to today)",
    )

    list_parser = subparsers.add_parser("list", help="Show all transactions")
    list_parser.add_argument("--latest", action="store_true", help="Show latest entries first")

    subparsers.add_parser("summary", help="Show totals and category breakdowns")
    subparsers.add_parser("init", help="Create an empty ledger if one does not exist")

    return parser


def handle_args(args: argparse.Namespace) -> None:
    data_file: Path = args.data_file
    if args.command == "add":
        transaction = add_transaction(
            kind=args.kind,
            amount=args.amount,
            category=args.category,
            description=args.description,
            date_str=args.date_str,
            data_file=data_file,
        )
        print("Recorded:")
        _print_transactions([transaction])
    elif args.command == "list":
        transactions = _load_transactions(data_file)
        if args.latest:
            transactions = list(sorted(transactions, key=lambda t: t.date, reverse=True))
        else:
            transactions = list(sorted(transactions, key=lambda t: t.date))
        if not transactions:
            print("No transactions found. Use 'add' to record income or expenses.")
            return
        _print_transactions(transactions)
    elif args.command == "summary":
        transactions = _load_transactions(data_file)
        if not transactions:
            print("No transactions to summarize yet.")
            return
        _print_summary(transactions)
    elif args.command == "init":
        if data_file.exists():
            print(f"Ledger already exists at {data_file}")
        else:
            _save_transactions(data_file, [])
            print(f"Created new ledger at {data_file}")


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    handle_args(args)


if __name__ == "__main__":
    main()
