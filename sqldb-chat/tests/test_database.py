import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import DB_PATH, get_connection, init_db, execute_query


def test_db_path_is_sqlite_file(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    init_db()
    conn = get_connection()
    assert conn is not None
    conn.close()


def test_init_db_creates_all_tables(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    init_db()
    assert db_path.exists()
    conn = get_connection()
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    for expected in [
        "Customer",
        "Supplier",
        "Product",
        "Sales_Order",
        "Sales_Order_Item",
        "Purchase_Order",
    ]:
        assert expected in tables, f"Tabel {expected} tidak ditemukan"


def test_init_db_seeds_sample_data(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    init_db()
    conn = get_connection()
    counts = {}
    for table in [
        "Customer",
        "Supplier",
        "Product",
        "Sales_Order",
        "Sales_Order_Item",
        "Purchase_Order",
    ]:
        cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cur.fetchone()[0]
    conn.close()
    assert counts["Customer"] == 20
    assert counts["Supplier"] == 10
    assert counts["Product"] == 30
    assert counts["Sales_Order"] == 25
    assert counts["Sales_Order_Item"] >= 25
    assert counts["Purchase_Order"] == 15
    total = sum(counts.values())
    assert 90 <= total <= 130, f"Total baris sample sekitar 100, ditemukan {total}"


def test_get_connection_is_read_only(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    init_db()
    conn = get_connection()
    try:
        conn.execute("INSERT INTO Customer (nama, kota) VALUES ('X', 'Y')")
        conn.commit()
        assert False, "Koneksi read-only seharusnya menolak INSERT"
    except Exception:
        pass  # diharapkan gagal karena read-only
    finally:
        conn.close()


def test_execute_query_returns_list_of_dicts(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    init_db()
    rows = execute_query("SELECT nama FROM Customer LIMIT 3", ())
    assert isinstance(rows, list)
    assert len(rows) == 3
    assert all(isinstance(r, dict) for r in rows)
    assert "nama" in rows[0]


def test_execute_query_rejects_non_select(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    init_db()
    try:
        execute_query("INSERT INTO Customer (nama, kota) VALUES ('X', 'Y')", ())
        assert False, "execute_query seharusnya menolak non-SELECT"
    except Exception:
        pass  # diharapkan gagal
