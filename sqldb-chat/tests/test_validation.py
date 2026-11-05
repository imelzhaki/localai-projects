import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validation import (
    check_aggregate_in_where,
    normalize_sql_for_sqlite,
    validate_columns_against_schema,
    validate_sql,
)

SCHEMA_DOCS = [
    {
        "table": "Customer",
        "columns": [
            "customer_id: ID pelanggan (primary key)",
            "nama: Nama pelanggan",
            "kota: Kota pelanggan",
            "telepon: Nomor telepon pelanggan",
            "email: Alamat email pelanggan",
            "tanggal_gabung: Tanggal pelanggan bergabung",
        ],
    },
    {
        "table": "Product",
        "columns": [
            "product_id: ID produk (primary key)",
            "nama: Nama produk",
            "kategori: Kategori produk (Elektronik, Aksesori, Komputer)",
            "harga: Harga jual produk",
            "stok: Stok tersedia produk",
        ],
    },
    {
        "table": "Sales_Order",
        "columns": [
            "order_id: ID pesanan (primary key)",
            "customer_id: ID pelanggan (foreign key ke Customer)",
            "tanggal: Tanggal transaksi",
            "total: Total nilai transaksi",
            "status: Status transaksi (Lunas, dll.)",
        ],
    },
]


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


def test_normalize_sql_for_sqlite_extract_month():
    sql = "SELECT EXTRACT(MONTH FROM so.tanggal) FROM Sales_Order so;"
    result = normalize_sql_for_sqlite(sql)
    assert "EXTRACT" not in result.upper()
    assert "strftime('%m', so.tanggal)" in result


def test_normalize_sql_for_sqlite_extract_year():
    sql = "SELECT EXTRACT(YEAR FROM so.tanggal) FROM Sales_Order so;"
    result = normalize_sql_for_sqlite(sql)
    assert "EXTRACT" not in result.upper()
    assert "strftime('%Y', so.tanggal)" in result


def test_normalize_sql_for_sqlite_extract_day():
    sql = "SELECT EXTRACT(DAY FROM so.tanggal) FROM Sales_Order so;"
    result = normalize_sql_for_sqlite(sql)
    assert "EXTRACT" not in result.upper()
    assert "strftime('%d', so.tanggal)" in result


def test_normalize_sql_for_sqlite_qualified_column():
    sql = "SELECT EXTRACT(MONTH FROM c.tanggal) FROM Customer c;"
    result = normalize_sql_for_sqlite(sql)
    assert "strftime('%m', c.tanggal)" in result


def test_normalize_sql_for_sqlite_no_extract_unchanged():
    sql = "SELECT * FROM Customer WHERE kota = 'Jakarta';"
    result = normalize_sql_for_sqlite(sql)
    assert result == sql


def test_normalize_sql_for_sqlite_empty_string():
    result = normalize_sql_for_sqlite("")
    assert result == ""


def test_check_aggregate_in_where_max():
    sql = "SELECT * FROM Sales_Order WHERE MAX(total) > 100;"
    bad, error = check_aggregate_in_where(sql)
    assert bad is True
    assert error is not None


def test_check_aggregate_in_where_min():
    sql = "SELECT * FROM Sales_Order WHERE MIN(tanggal) = '2023-01-01';"
    bad, error = check_aggregate_in_where(sql)
    assert bad is True
    assert error is not None


def test_check_aggregate_in_where_sum():
    sql = "SELECT * FROM Sales_Order WHERE SUM(total) > 1000;"
    bad, error = check_aggregate_in_where(sql)
    assert bad is True
    assert error is not None


def test_check_aggregate_in_where_count():
    sql = "SELECT * FROM Sales_Order WHERE COUNT(*) > 5;"
    bad, error = check_aggregate_in_where(sql)
    assert bad is True
    assert error is not None


def test_check_aggregate_in_where_avg():
    sql = "SELECT * FROM Sales_Order WHERE AVG(total) > 100;"
    bad, error = check_aggregate_in_where(sql)
    assert bad is True
    assert error is not None


def test_check_aggregate_in_where_no_aggregate():
    sql = "SELECT * FROM Sales_Order WHERE total > 100;"
    bad, error = check_aggregate_in_where(sql)
    assert bad is False
    assert error is None


def test_check_aggregate_in_where_aggregate_in_select_ok():
    sql = "SELECT MAX(total) FROM Sales_Order WHERE total > 100;"
    bad, error = check_aggregate_in_where(sql)
    assert bad is False
    assert error is None


def test_check_aggregate_in_where_no_where_clause():
    sql = "SELECT * FROM Sales_Order;"
    bad, error = check_aggregate_in_where(sql)
    assert bad is False
    assert error is None


def test_check_aggregate_in_where_empty_string():
    bad, error = check_aggregate_in_where("")
    assert bad is False
    assert error is None


def test_validate_columns_against_schema_wrong_table():
    """c.kategori salah karena kategori ada pada Product, bukan Customer."""
    sql = "SELECT SUM(so.total) FROM Sales_Order so JOIN Customer c ON so.customer_id = c.customer_id WHERE c.kategori = 'Elektronik';"
    bad, error = validate_columns_against_schema(sql, SCHEMA_DOCS)
    assert bad is True
    assert error is not None
    assert "kategori" in error
    assert "Customer" in error


def test_validate_columns_against_schema_correct_table():
    """c.kota benar karena kota ada pada Customer."""
    sql = "SELECT * FROM Customer c WHERE c.kota = 'Jakarta';"
    bad, error = validate_columns_against_schema(sql, SCHEMA_DOCS)
    assert bad is False
    assert error is None


def test_validate_columns_against_schema_unaliased_column():
    """Kolom tanpa alias tidak dicek (tidak ada alias yang cocok)."""
    sql = "SELECT * FROM Customer WHERE kota = 'Jakarta';"
    bad, error = validate_columns_against_schema(sql, SCHEMA_DOCS)
    assert bad is False
    assert error is None


def test_validate_columns_against_schema_product_kategori():
    """p.kategori benar karena kategori ada pada Product."""
    sql = "SELECT * FROM Product p WHERE p.kategori = 'Elektronik';"
    bad, error = validate_columns_against_schema(sql, SCHEMA_DOCS)
    assert bad is False
    assert error is None


def test_validate_columns_against_schema_unknown_column():
    """c.nama_salah tidak ada pada Customer."""
    sql = "SELECT * FROM Customer c WHERE c.nama_salah = 'Budi';"
    bad, error = validate_columns_against_schema(sql, SCHEMA_DOCS)
    assert bad is True
    assert error is not None


def test_validate_columns_against_schema_empty_sql():
    bad, error = validate_columns_against_schema("", SCHEMA_DOCS)
    assert bad is False
    assert error is None


def test_validate_columns_against_schema_empty_schema():
    bad, error = validate_columns_against_schema("SELECT * FROM Customer c WHERE c.kota = 'Jakarta';", [])
    assert bad is False
    assert error is None