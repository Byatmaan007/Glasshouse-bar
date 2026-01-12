# Restaurant Expense Tracker

A lightweight command-line utility for recording incoming revenue and outgoing expenses for the restaurant. Data is stored in a JSON file (`expenses.json` by default) located next to the script.

## Prerequisites

- Python 3.10 or newer (comes with macOS/Linux by default; Windows users can install from [python.org](https://www.python.org/downloads/)).
- No extra packages are required—everything uses Python's standard library.

## Step-by-step: run the tracker

1. **Open a terminal** and change into this project folder. On Windows you can use *Command Prompt* or *PowerShell*.

   ```bash
   cd path/to/Glasshouse-bar
   ```

2. **Initialize the ledger file** (creates `expenses.json` next to the script):

   ```bash
   python expense_tracker.py init
   ```

   You should see `Created new ledger at ...` the first time. If it already exists, the command tells you.

3. **Add income or expenses**. Amounts are positive; expenses are shown as negatives when listed.

   ```bash
   python expense_tracker.py add income 2000 "Saturday dinner service" --category dining
   python expense_tracker.py add expense 350 "Produce order" --category supplies --date 2024-11-25
   ```

4. **See what you have recorded**:

   ```bash
   python expense_tracker.py list
   ```

   Add `--latest` if you want the newest transactions first.

5. **Get totals and category breakdowns**:

   ```bash
   python expense_tracker.py summary
   ```

6. **Use a different ledger file (optional)** if you want to keep separate books or test safely:

   ```bash
   python expense_tracker.py --data-file /tmp/my_ledger.json add expense 50 "Coffee beans" --category bar
   ```

   The file will be created automatically when you run `init` or add the first transaction with `--data-file`.

If you forget a command, run `python expense_tracker.py --help` for a full list.

## How the data file works

- The tracker writes plain JSON to `expenses.json` by default.
- You can delete that file to start over, or pass `--data-file some_path.json` to keep multiple ledgers.
- Entries are stored as positive numbers; the list view shows expenses as negative for readability.

## Run the automated tests

The tests confirm the CLI and calculations work. From the project root run:

```bash
python -m pytest -q
```

> If `pytest` is not installed, install it with `python -m pip install pytest` and run the command again.

## Common tips for beginners

- If `python` is not found, try `python3` in the commands above.
- On Windows, replace `/tmp/my_ledger.json` with a Windows path like `C:\\temp\\my_ledger.json`.
- You can open `expenses.json` in any text editor to review or back up your data.
