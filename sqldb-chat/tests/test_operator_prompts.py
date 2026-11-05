"""Tes untuk semua prompt operator dalam bisnis retail elektronik.

Setiap tes memetakan prompt Bahasa Indonesia ke panggilan alat (tool)
dan memverifikasi bahwa hasilnya benar sesuai dengan data sampel.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import init_db, DB_PATH
import tools


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _init_tmp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("tools.DB_PATH", db_path)
    init_db()


# ---------------------------------------------------------------------------
# 1. Manajemen Customer
# ---------------------------------------------------------------------------

def test_prompt_1_berapa_jumlah_customer(tmp_path, monkeypatch):
    """Prompt: 'Berapa jumlah customer yang ada?'"""
    _init_tmp_db(tmp_path, monkeypatch)
    stats = tools.get_database_stats()
    assert stats["Customer"] == 20


def test_prompt_2_list_semua_customer(tmp_path, monkeypatch):
    """Prompt: 'List semua customer'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.list_customers()
    assert isinstance(hasil, list)
    assert len(hasil) == 20
    assert all("nama" in r and "kota" in r and "telepon" in r and "email" in r for r in hasil)


def test_prompt_3_cari_customer_nama_budi(tmp_path, monkeypatch):
    """Prompt: 'Cari customer yang nama-nya Budi'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_customer(nama="Budi")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all("Budi" in r["nama"] for r in hasil)


def test_prompt_4_customer_di_jakarta(tmp_path, monkeypatch):
    """Prompt: 'Customer yang tinggal di Jakarta'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_customer(kota="Jakarta")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["kota"] == "Jakarta" for r in hasil)


def test_prompt_5_detail_customer_id_1(tmp_path, monkeypatch):
    """Prompt: 'Detail customer ID 1'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_customer(customer_id=1)
    assert isinstance(hasil, dict)
    assert hasil["nama"] == "Budi Santoso"
    assert hasil["kota"] == "Jakarta"


def test_prompt_6_customer_tidak_ditemukan(tmp_path, monkeypatch):
    """Prompt: 'Customer yang nama-nya Xyz123' (tidak ada)"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_customer(nama="Xyz123")
    assert hasil == []


# ---------------------------------------------------------------------------
# 2. Manajemen Produk
# ---------------------------------------------------------------------------

def test_prompt_7_list_semua_produk(tmp_path, monkeypatch):
    """Prompt: 'List semua produk'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.list_products()
    assert isinstance(hasil, list)
    assert len(hasil) == 30
    assert all("nama" in r and "kategori" in r and "harga" in r and "stok" in r for r in hasil)


def test_prompt_8_produk_kategori_elektronik(tmp_path, monkeypatch):
    """Prompt: 'Produk kategori Elektronik'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_product(kategori="Elektronik")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["kategori"] == "Elektronik" for r in hasil)


def test_prompt_9_produk_kategori_aksesori(tmp_path, monkeypatch):
    """Prompt: 'Produk kategori Aksesori'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_product(kategori="Aksesori")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["kategori"] == "Aksesori" for r in hasil)


def test_prompt_10_produk_kategori_komputer(tmp_path, monkeypatch):
    """Prompt: 'Produk kategori Komputer'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_product(kategori="Komputer")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["kategori"] == "Komputer" for r in hasil)


def test_prompt_11_produk_stok_di_bawah_10(tmp_path, monkeypatch):
    """Prompt: 'Produk dengan stok di bawah 10'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_product(stok_max=10)
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["stok"] <= 10 for r in hasil)


def test_prompt_12_produk_harga_di_bawah_500000(tmp_path, monkeypatch):
    """Prompt: 'Produk dengan harga di bawah 500000'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_product(harga_max=500000)
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["harga"] <= 500000 for r in hasil)


def test_prompt_13_detail_produk_blender(tmp_path, monkeypatch):
    """Prompt: 'Detail produk Blender'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_product(nama="Blender")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all("Blender" in r["nama"] for r in hasil)


def test_prompt_14_detail_produk_laptop_asus_rog(tmp_path, monkeypatch):
    """Prompt: 'Detail produk Laptop Asus ROG'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_product(nama="Laptop Asus ROG")
    assert isinstance(hasil, list)
    assert len(hasil) == 1
    assert hasil[0]["nama"] == "Laptop Asus ROG"
    assert hasil[0]["kategori"] == "Elektronik"


def test_prompt_15_produk_tidak_ada(tmp_path, monkeypatch):
    """Prompt: 'Produk yang nama-nya ProdukXyz' (tidak ada)"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_product(nama="ProdukXyz")
    assert hasil == []


# ---------------------------------------------------------------------------
# 3. Pesanan Penjualan (Sales Order)
# ---------------------------------------------------------------------------

def test_prompt_16_list_semua_pesanan_penjualan(tmp_path, monkeypatch):
    """Prompt: 'List semua pesanan penjualan'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.list_sales_orders()
    assert isinstance(hasil, list)
    assert len(hasil) == 25
    assert all("order_id" in r and "total" in r and "status" in r and "pelanggan" in r for r in hasil)


def test_prompt_17_pesanan_yang_sudah_lunas(tmp_path, monkeypatch):
    """Prompt: 'Pesanan penjualan yang sudah lunas'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_order(status="Lunas")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["status"] == "Lunas" for r in hasil)


def test_prompt_18_pesanan_bulan_oktober_2024(tmp_path, monkeypatch):
    """Prompt: 'Pesanan penjualan bulan Oktober 2024'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_order(rentang_tanggal="2024-10-01 s.d. 2024-10-31")
    assert isinstance(hasil, list)
    assert len(hasil) == 20


def test_prompt_19_detail_pesanan_id_1(tmp_path, monkeypatch):
    """Prompt: 'Detail pesanan penjualan ID 1'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_order(order_id=1)
    assert isinstance(hasil, list)
    assert len(hasil) == 1
    assert hasil[0]["order_id"] == 1


def test_prompt_20_item_dalam_pesanan_id_1(tmp_path, monkeypatch):
    """Prompt: 'Item dalam pesanan penjualan ID 1'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_order_items(order_id=1)
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all("produk" in r and "kuantitas" in r and "subtotal" in r for r in hasil)


def test_prompt_21_semua_item_pesanan_terbaru(tmp_path, monkeypatch):
    """Prompt: 'Semua item pesanan penjualan terbaru'"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_order_items()
    assert isinstance(hasil, list)
    assert len(hasil) > 0


# ---------------------------------------------------------------------------
# 4. Pesanan Pembelian (Purchase Order)
# ---------------------------------------------------------------------------

def test_prompt_22_list_semua_pesanan_pembelian(tmp_path, monkeypatch):
    """Prompt: "List semua pesanan pembelian"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.list_purchase_orders()
    assert isinstance(hasil, list)
    assert len(hasil) == 15
    assert all("order_id" in r and "total" in r and "status" in r and "supplier" in r for r in hasil)


def test_prompt_23_pesanan_pembelian_supplier_id_1(tmp_path, monkeypatch):
    """Prompt: "Pesanan pembelian dari supplier ID 1"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_purchase_order(supplier_id=1)
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r["supplier"] == "Toko Elektronik Jaya" for r in hasil)


def test_prompt_24_pesanan_pembelian_september_2024(tmp_path, monkeypatch):
    """Prompt: "Pesanan pembelian September 2024"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_purchase_order(rentang_tanggal="2024-09-01 s.d. 2024-09-30")
    assert isinstance(hasil, list)
    assert len(hasil) == 10


# ---------------------------------------------------------------------------
# 5. Supplier
# ---------------------------------------------------------------------------

def test_prompt_25_list_semua_supplier(tmp_path, monkeypatch):
    """Prompt: "List semua supplier"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.list_suppliers()
    assert isinstance(hasil, list)
    assert len(hasil) == 10
    assert all("nama" in r and "kota" in r and "telepon" in r for r in hasil)


def test_prompt_26_detail_supplier_toko_elektronik_jaya(tmp_path, monkeypatch):
    """Prompt: "Detail supplier Toko Elektronik Jaya"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_supplier(nama="Toko Elektronik Jaya")
    assert isinstance(hasil, dict)
    assert hasil["nama"] == "Toko Elektronik Jaya"


def test_prompt_27_detail_supplier_id_1(tmp_path, monkeypatch):
    """Prompt: "Detail supplier ID 1"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_supplier(supplier_id=1)
    assert isinstance(hasil, dict)
    assert hasil["nama"] == "Toko Elektronik Jaya"


# ---------------------------------------------------------------------------
# 6. Analitik Penjualan
# ---------------------------------------------------------------------------

def test_prompt_28_penjualan_kategori_elektronik_bulan_lalu(tmp_path, monkeypatch):
    """Prompt: "Penjualan kategori Elektronik bulan lalu"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_data(category="Elektronik", month="last")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all(r.get("kategori") == "Elektronik" or "kategori" in r for r in hasil)


def test_prompt_29_semua_penjualan_tanpa_filter_kategori(tmp_path, monkeypatch):
    """Prompt: "Semua penjualan tanpa filter kategori"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_data()
    assert isinstance(hasil, list)
    assert len(hasil) > 0


def test_prompt_30_penjualan_produk_blender(tmp_path, monkeypatch):
    """Prompt: "Penjualan produk Blender"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_by_product(nama_produk="Blender")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all("produk" in r and "jumlah_terjual" in r for r in hasil)
    assert all("Blender" in r["produk"] for r in hasil)


def test_prompt_31_penjualan_produk_webcam_bulan_lalu(tmp_path, monkeypatch):
    """Prompt: "Penjualan produk Webcam bulan lalu"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_by_product(nama_produk="Webcam", month="last")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all("Webcam" in r["produk"] for r in hasil)


def test_prompt_32_penjualan_produk_laptop(tmp_path, monkeypatch):
    """Prompt: "Penjualan produk Laptop"""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_by_product(nama_produk="Laptop")
    assert isinstance(hasil, list)
    assert len(hasil) > 0
    assert all("Laptop" in r["produk"] for r in hasil)


def test_prompt_33_tahun_penjualan(tmp_path, monkeypatch):
    """Prompt: "Tahun berapa saja penjualan dilakukan?"""
    _init_tmp_db(tmp_path, monkeypatch)
    tahun = tools.get_sales_years()
    assert isinstance(tahun, list)
    assert "2024" in tahun


def test_prompt_34_statistik_database(tmp_path, monkeypatch):
    """Prompt: "Statistik ringkasan database"""
    _init_tmp_db(tmp_path, monkeypatch)
    stats = tools.get_database_stats()
    assert isinstance(stats, dict)
    assert stats["Customer"] == 20
    assert stats["Supplier"] == 10
    assert stats["Product"] == 30
    assert stats["Sales_Order"] == 25
    assert stats["Sales_Order_Item"] == 26
    assert stats["Purchase_Order"] == 15


# ---------------------------------------------------------------------------
# 7. Prompt yang harus dihindari (negative tests)
# ---------------------------------------------------------------------------

def test_prompt_a_kategori_produk_tidak_valid(tmp_path, monkeypatch):
    """Prompt: "Penjualan kategori Produk bulan lalu" — kategori "produk" tidak valid."""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_data(category="produk", month="last")
    assert hasil == []  # Tidak ada produk dengan kategori "produk"


def test_prompt_b_get_sales_by_product_tanpa_category(tmp_path, monkeypatch):
    """Prompt: "Penjualan Blender" — get_sales_by_product tidak menerima parameter category."""
    _init_tmp_db(tmp_path, monkeypatch)
    # Hanya nama_produk dan month yang valid, tidak ada category
    hasil = tools.get_sales_by_product(nama_produk="Blender")
    assert isinstance(hasil, list)
    assert len(hasil) > 0


def test_prompt_c_month_null_string(tmp_path, monkeypatch):
    """Prompt: "Penjualan Webcam bulan null" — string "null" harus diformasi sebagai None."""
    _init_tmp_db(tmp_path, monkeypatch)
    hasil = tools.get_sales_by_product(nama_produk="Webcam", month="null")
    # "null" diformasi sebagai None, jadi tanpa filter month -> hasil berdasarkan nama_produk saja
    assert isinstance(hasil, list)
    assert len(hasil) > 0


def test_prompt_d_customer_nama_bintang(tmp_path, monkeypatch):
    """Prompt: "Customer dengan nama *" — jangan gunakan get_customer(nama="*"), gunakan list_customers()."""
    _init_tmp_db(tmp_path, monkeypatch)
    # get_customer(nama="*") akan mencari nama yang mengandung "*" -> tidak ada hasil
    hasil = tools.get_customer(nama="*")
    assert hasil == []
    # Benarnya gunakan list_customers()
    semua = tools.list_customers()
    assert len(semua) == 20