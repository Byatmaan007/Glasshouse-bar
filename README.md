# Restaurant Expense Tracker

A lightweight command-line utility for recording incoming revenue and outgoing expenses for the restaurant. Data is stored in a JSON file (`expenses.json` by default) located next to the script.

## Quick start

```bash
python expense_tracker.py init
python expense_tracker.py add income 2000 "Saturday dinner service" --category dining
python expense_tracker.py add expense 350 "Produce order" --category supplies --date 2024-11-25
python expense_tracker.py list
python expense_tracker.py summary
```

Use `--data-file` to point the tracker at a different ledger file if you want to keep separate books or run tests:

```bash
python expense_tracker.py add expense 50 "Coffee beans" --category bar --data-file /tmp/ledger.json
```

## Commands

- `init`: create an empty ledger file if one does not already exist.
- `add <income|expense> <amount> <description> [--category NAME] [--date YYYY-MM-DD] [--data-file PATH]`
- `list [--latest] [--data-file PATH]`: show transactions in chronological (or reverse) order.
- `summary [--data-file PATH]`: display income, expenses, net, and per-category totals.

Amounts are stored as positive numbers; expenses are shown as negatives in the list view to differentiate them from income.
