import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import DB_PATH, init_db
import schema


def test_build_schema_docs_returns_table_docs(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("schema.DB_PATH", db_path)
    init_db()

    docs = schema.build_schema_docs()

    assert isinstance(docs, list)
    assert len(docs) > 0
    table_names = {d["table"] for d in docs}
    assert "Customer" in table_names
    assert "Product" in table_names
    for doc in docs:
        assert "table" in doc
        assert "purpose" in doc
        assert "columns" in doc
        assert "value_legend" in doc


def test_build_schema_docs_includes_column_descriptions(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("schema.DB_PATH", db_path)
    init_db()

    docs = schema.build_schema_docs()
    customer_doc = next(d for d in docs if d["table"] == "Customer")
    columns_text = " ".join(customer_doc["columns"])
    assert "customer_id" in columns_text
    assert "nama" in columns_text
    assert "kota" in columns_text


def test_build_schema_docs_includes_value_legend(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("schema.DB_PATH", db_path)
    init_db()

    docs = schema.build_schema_docs()
    product_doc = next(d for d in docs if d["table"] == "Product")
    assert "kategori" in product_doc.get("value_legend", {})
