import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app


def test_process_question_returns_result_dict(monkeypatch, tmp_path):
    """process_question mengembalikan dict dengan kunci yang diharapkan."""

    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.DB_PATH", db_path)
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("schema.DB_PATH", db_path)
    monkeypatch.setattr("retrieval.DB_PATH", db_path)
    monkeypatch.setattr("execution.DB_PATH", db_path)

    from database import init_db
    init_db()

    monkeypatch.setattr(
        app,
        "retrieve_schema_docs",
        lambda question, top_k=3: [
            {
                "table": "Customer",
                "document": "Tabel: Customer. Tujuan: Tabel pelanggan. Kolom: customer_id: ID, nama: Nama, kota: Kota.",
            }
        ],
    )

    monkeypatch.setattr(
        app,
        "generate_sql",
        lambda question, schema_docs, fewshot_examples: "SELECT * FROM Customer WHERE kota = 'Jakarta';",
    )

    monkeypatch.setattr(
        app,
        "validate_sql",
        lambda sql: {"valid": True, "error": None, "sql": sql},
    )

    monkeypatch.setattr(
        app,
        "critique_sql",
        lambda question, sql, schema_docs: {"corrected": False, "sql": sql, "error": None},
    )

    monkeypatch.setattr(
        app,
        "execute_select",
        lambda sql: {"ok": True, "rows": [{"customer_id": 1, "nama": "Budi", "kota": "Jakarta"}], "error": None},
    )

    result = app.process_question("Tampilkan pelanggan di Jakarta")

    assert isinstance(result, dict)
    assert "question" in result
    assert "sql" in result
    assert "rows" in result
    assert "error" in result
    assert result["error"] is None
    assert len(result["rows"]) == 1
    assert result["rows"][0]["nama"] == "Budi"


def test_process_question_handles_validation_error(monkeypatch, tmp_path):
    """process_question menangani kesalahan validasi SQL."""

    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.DB_PATH", db_path)
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("schema.DB_PATH", db_path)
    monkeypatch.setattr("retrieval.DB_PATH", db_path)
    monkeypatch.setattr("execution.DB_PATH", db_path)

    from database import init_db
    init_db()

    monkeypatch.setattr(
        app,
        "retrieve_schema_docs",
        lambda question, top_k=3: [],
    )
    monkeypatch.setattr(
        app,
        "generate_sql",
        lambda question, schema_docs, fewshot_examples: "INSERT INTO Customer VALUES (1);",
    )
    monkeypatch.setattr(
        app,
        "validate_sql",
        lambda sql: {"valid": False, "error": "Hanya SELECT yang diizinkan", "sql": sql},
    )

    result = app.process_question("Test")

    assert result["error"] is not None
    assert "SELECT" in result["error"] or "select" in result["error"]
    assert result["rows"] is None or result["rows"] == []
