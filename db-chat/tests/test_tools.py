import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import init_db, DB_PATH
import tools


def test_get_sales_data_by_category(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_sales_data(category="Elektronik", month="last")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all("kategori" in r or "nama" in r for r in hasil)


def test_get_sales_data_empty_category(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_sales_data(category="TidakAda", month="last")
    assert hasil == [] or hasil == "Tidak ada data"


def test_get_customer_by_id(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_customer(customer_id=1)
    assert isinstance(hasil, dict)
    assert hasil["nama"] == "Budi Santoso"


def test_get_customer_not_found(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_customer(customer_id=9999)
    assert hasil == {} or hasil == "Pelanggan tidak ditemukan"


def test_get_product_by_category(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_product(kategori="Elektronik")
    assert isinstance(hasil, list)
    assert len(hasil) > 0


def test_get_supplier_by_id(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_supplier(supplier_id=1)
    assert isinstance(hasil, dict)
    assert hasil["nama"] == "Toko Elektronik Jaya"


def test_list_customers(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.list_customers()
    assert isinstance(hasil, list)
    assert len(hasil) == 20
    assert all("nama" in r and "kota" in r for r in hasil)


def test_list_sales_orders(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.list_sales_orders()
    assert isinstance(hasil, list)
    assert len(hasil) == 25
    assert all("order_id" in r and "total" in r and "pelanggan" in r for r in hasil)


def test_list_purchase_orders(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.list_purchase_orders()
    assert isinstance(hasil, list)
    assert len(hasil) == 15
    assert all("order_id" in r and "total" in r and "supplier" in r for r in hasil)


def test_tools_schemas_are_valid():
    """Setiap alat dalam TOOLS memiliki nama, deskripsi, dan parameter."""
    for alat in tools.TOOLS:
        fn = alat["function"]
        assert "name" in fn
        assert "description" in fn
        assert "parameters" in fn
        assert "type" in fn["parameters"]
        assert "properties" in fn["parameters"]


def test_list_suppliers(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.list_suppliers()
    assert isinstance(hasil, list)
    assert len(hasil) == 10
    assert all("nama" in r and "kota" in r and "telepon" in r for r in hasil)


def test_list_products(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.list_products()
    assert isinstance(hasil, list)
    assert len(hasil) == 30
    assert all("nama" in r and "kategori" in r and "harga" in r and "stok" in r for r in hasil)


def test_list_products_by_kategori(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.list_products(kategori="Elektronik")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["kategori"] == "Elektronik" for r in hasil)


def test_list_products_by_kategori_tidak_ditemukan(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.list_products(kategori="TidakAda")
    assert hasil == []


def test_list_products_by_stok_max(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.list_products(stok_max=10)
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["stok"] <= 10 for r in hasil)


def test_list_products_by_harga_max(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.list_products(harga_max=500000)
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["harga"] <= 500000 for r in hasil)


def test_get_sales_by_product(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_sales_by_product(nama_produk="Blender")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all("produk" in r and "jumlah_terjual" in r for r in hasil)
    assert all("Blender" in r["produk"] for r in hasil)


def test_get_sales_by_product_not_found(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_sales_by_product(nama_produk="ProdukTidakAda")
    assert hasil == []


def test_get_sales_years(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    tahun = tools.get_sales_years()
    assert isinstance(tahun, list)
    assert "2024" in tahun


def test_get_sales_order_items_by_order(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_sales_order_items(order_id=1)
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all("produk" in r and "kuantitas" in r and "subtotal" in r for r in hasil)


def test_get_sales_order_items_all(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_sales_order_items()
    assert isinstance(hasil, list)
    assert len(hasil) > 0


def test_get_database_stats(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    stats = tools.get_database_stats()
    assert isinstance(stats, dict)
    assert stats["Customer"] == 20
    assert stats["Supplier"] == 10
    assert stats["Product"] == 30
    assert stats["Sales_Order"] == 25
    assert stats["Sales_Order_Item"] == 26
    assert stats["Purchase_Order"] == 15


def test_get_customer_by_kota(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_customer(kota="Jakarta")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["kota"] == "Jakarta" for r in hasil)


def test_get_sales_order_by_status(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_sales_order(status="Lunas")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["status"] == "Lunas" for r in hasil)


def test_get_product_by_stok_max(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_product(stok_max=5)
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["stok"] <= 5 for r in hasil)


def test_get_product_by_harga_max(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()
    hasil = tools.get_product(harga_max=1000000)
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["harga"] <= 1000000 for r in hasil)
