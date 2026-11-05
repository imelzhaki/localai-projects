import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validation import validate_sql


def test_validate_sql_accepts_valid_select():
    result = validate_sql("SELECT * FROM Customer WHERE kota = 'Jakarta';")
    assert result["valid"] is True
    assert result["error"] is None


def test_validate_sql_rejects_insert():
    result = validate_sql("INSERT INTO Customer (nama) VALUES ('Test');")
    assert result["valid"] is False
    assert "non-select" in result["error"].lower() or "insert" in result["error"].lower()


def test_validate_sql_rejects_delete():
    result = validate_sql("DELETE FROM Customer WHERE customer_id = 1;")
    assert result["valid"] is False


def test_validate_sql_rejects_update():
    result = validate_sql("UPDATE Customer SET nama = 'Test' WHERE customer_id = 1;")
    assert result["valid"] is False


def test_validate_sql_rejects_invalid_syntax():
    result = validate_sql("SELECT * FROM NonExistentTable WHERE ;")
    assert result["valid"] is False
    assert result["error"] is not None


def test_validate_sql_rejects_empty_string():
    result = validate_sql("")
    assert result["valid"] is False
    assert result["error"] is not None