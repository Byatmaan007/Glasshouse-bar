import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import expense_tracker as et


def test_add_and_list_transactions(tmp_path: Path):
    data_file = tmp_path / "ledger.json"

    et.add_transaction(
        kind="income",
        amount=1200.50,
        category="dining",
        description="Saturday dinner service",
        date_str="2024-11-23",
        data_file=data_file,
    )
    et.add_transaction(
        kind="expense",
        amount=300.25,
        category="supplies",
        description="Weekly produce order",
        date_str="2024-11-24",
        data_file=data_file,
    )

    transactions = et._load_transactions(data_file)
    assert len(transactions) == 2
    assert transactions[0].kind == "income"
    assert transactions[1].kind == "expense"


def test_summary_breakdown(tmp_path: Path):
    data_file = tmp_path / "ledger.json"
    et.add_transaction(
        kind="income",
        amount=1000,
        category="events",
        description="Catering deposit",
        date_str="2024-11-20",
        data_file=data_file,
    )
    et.add_transaction(
        kind="expense",
        amount=400,
        category="payroll",
        description="Bartender shift",
        date_str="2024-11-21",
        data_file=data_file,
    )

    income_total, expense_total, net, categories = et.summarize(et._load_transactions(data_file))

    assert income_total == pytest.approx(1000)
    assert expense_total == pytest.approx(400)
    assert net == pytest.approx(600)
    assert categories["events"] == pytest.approx(1000)
    assert categories["payroll"] == pytest.approx(-400)


def test_invalid_amount_raises(tmp_path: Path):
    data_file = tmp_path / "ledger.json"
    with pytest.raises(ValueError):
        et.add_transaction(
            kind="expense",
            amount=-10,
            category="supplies",
            description="Bad input",
            data_file=data_file,
        )


def test_init_command_creates_file(tmp_path: Path, capsys):
    data_file = tmp_path / "ledger.json"
    args = et._build_parser().parse_args(["--data-file", str(data_file), "init"])
    et.handle_args(args)

    assert data_file.exists()
    with open(data_file, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    assert payload == []
    captured = capsys.readouterr()
    assert "Created new ledger" in captured.out
