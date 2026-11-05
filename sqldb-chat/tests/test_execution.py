import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import DB_PATH, init_db
import execution


def test_execute_select_returns_rows(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("execution.DB_PATH", db_path)
    init_db()

    result = execution.execute_select("SELECT * FROM Customer LIMIT 3;")
    assert result["ok"] is True
    assert result["error"] is None
    assert isinstance(result["rows"], list)
    assert len(result["rows"]) == 3
    assert "customer_id" in result["rows"][0]
    assert "nama" in result["rows"][0]


def test_execute_select_rejects_non_select(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("execution.DB_PATH", db_path)
    init_db()

    result = execution.execute_select("INSERT INTO Customer (nama) VALUES ('Test');")
    assert result["ok"] is False
    assert result["error"] is not None
    assert result["rows"] is None


def test_execute_select_returns_empty_for_no_match(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("execution.DB_PATH", db_path)
    init_db()

    result = execution.execute_select(
        "SELECT * FROM Customer WHERE kota = 'NonExistentCity';"
    )
    assert result["ok"] is True
    assert result["error"] is None
    assert isinstance(result["rows"], list)
    assert len(result["rows"]) == 0


def test_execute_select_rejects_empty_sql(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("execution.DB_PATH", db_path)
    init_db()

    result = execution.execute_select("")
    assert result["ok"] is False
    assert result["error"] is not None
    assert result["rows"] is None