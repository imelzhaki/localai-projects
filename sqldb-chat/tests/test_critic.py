import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import critic


def test_critique_sql_returns_corrected_sql(monkeypatch):
    """Critik mengembalikan SQL yang dikoreksi saat ada kesalahan kolom."""

    def fake_llm_call(prompt):
        return "SELECT customer_id, nama, kota FROM Customer WHERE kota = 'Jakarta';"

    monkeypatch.setattr(critic, "_call_llm", fake_llm_call)

    question = "Tampilkan pelanggan di Jakarta"
    sql = "SELECT customer_id, nama, city FROM Customer WHERE kota = 'Jakarta';"
    schema_docs = [
        {
            "table": "Customer",
            "purpose": "Menyimpan data pelanggan toko elektronik.",
            "columns": [
                "customer_id: ID pelanggan (primary key)",
                "nama: Nama pelanggan",
                "kota: Kota pelanggan",
                "telepon: Nomor telepon pelanggan",
                "email: Alamat email pelanggan",
                "tanggal_gabung: Tanggal pelanggan bergabung",
            ],
            "value_legend": {},
        }
    ]

    result = critic.critique_sql(question, sql, schema_docs)
    assert result["corrected"] is True
    assert "city" not in result["sql"]
    assert "kota" in result["sql"]


def test_critique_sql_returns_original_when_correct(monkeypatch):
    """Critik mengembalikan SQL asli saat sudah benar."""

    def fake_llm_call(prompt):
        return "SELECT * FROM Customer WHERE kota = 'Jakarta';"

    monkeypatch.setattr(critic, "_call_llm", fake_llm_call)

    question = "Tampilkan pelanggan di Jakarta"
    sql = "SELECT * FROM Customer WHERE kota = 'Jakarta';"
    schema_docs = [
        {
            "table": "Customer",
            "purpose": "Menyimpan data pelanggan toko elektronik.",
            "columns": [
                "customer_id: ID pelanggan (primary key)",
                "nama: Nama pelanggan",
                "kota: Kota pelanggan",
            ],
            "value_legend": {},
        }
    ]

    result = critic.critique_sql(question, sql, schema_docs)
    assert result["corrected"] is False
    assert result["sql"] == sql


def test_critique_sql_handles_empty_sql(monkeypatch):
    """Critik menangani SQL kosong dengan mengembalikan error."""

    def fake_llm_call(prompt):
        return ""

    monkeypatch.setattr(critic, "_call_llm", fake_llm_call)

    result = critic.critique_sql("test", "", [])
    assert result["corrected"] is False
    assert result["sql"] == ""
    assert result["error"] is not None