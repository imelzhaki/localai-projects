import logging
from pathlib import Path

from sqlalchemy import create_engine, inspect

logger = logging.getLogger(__name__)

DB_PATH = Path("data/sqldb-chat.db")

_TABLE_PURPOSE = {
    "Customer": "Menyimpan data pelanggan toko elektronik.",
    "Supplier": "Menyimpan data supplier/vendor barang elektronik.",
    "Product": "Menyimpan katalog produk elektronik dan aksesori.",
    "Sales_Order": "Menyimpan header pesanan penjualan ke pelanggan.",
    "Sales_Order_Item": "Menyimpan item barang dalam setiap pesanan penjualan.",
    "Purchase_Order": "Menyimpan header pesanan pembelian dari supplier.",
}

_COLUMN_DESCRIPTIONS = {
    "customer_id": "ID pelanggan (primary key)",
    "nama": "Nama pelanggan",
    "kota": "Kota pelanggan",
    "telepon": "Nomor telepon pelanggan",
    "email": "Alamat email pelanggan",
    "tanggal_gabung": "Tanggal pelanggan bergabung",
    "supplier_id": "ID supplier (foreign key ke Supplier)",
    "kontak": "Kontak person supplier",
    "product_id": "ID produk (primary key)",
    "kategori": "Kategori produk (Elektronik, Aksesori, Komputer)",
    "harga": "Harga jual produk",
    "stok": "Stok tersedia produk",
    "order_id": "ID pesanan (primary key)",
    "tanggal": "Tanggal transaksi",
    "total": "Total nilai transaksi",
    "status": "Status transaksi (Lunas, dll.)",
    "item_id": "ID item pesanan (primary key)",
    "kuantitas": "Jumlah barang yang dipesan",
    "harga_satuan": "Harga per satuan barang",
}

_VALUE_LEGEND = {
    "Product.kategori": "Elektronik = produk elektronik, Aksesori = aksesori, Komputer = komputer",
    "Sales_Order.status": "Lunas = sudah dibayar",
    "Purchase_Order.status": "Lunas = sudah dibayar",
}


def build_schema_docs():
    """Introspeksi SQLite via SQLAlchemy Inspector dan buat dokumen metadata
    per tabel (bukan DDL mentah). Setiap dokumen berisi table, purpose,
    columns (daftar deskripsi kolom), dan value_legend.
    """
    uri = f"sqlite:///{DB_PATH.resolve()}"
    engine = create_engine(uri)
    inspector = inspect(engine)

    docs = []
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        col_descs = []
        for col in columns:
            col_name = col["name"]
            desc = _COLUMN_DESCRIPTIONS.get(
                col_name, f"Kolom {col_name} pada tabel {table_name}"
            )
            col_descs.append(f"{col_name}: {desc}")

        legend = {}
        for col in columns:
            key = f"{table_name}.{col['name']}"
            if key in _VALUE_LEGEND:
                legend[col["name"]] = _VALUE_LEGEND[key]

        docs.append(
            {
                "table": table_name,
                "purpose": _TABLE_PURPOSE.get(
                    table_name, f"Tabel {table_name} dalam database."
                ),
                "columns": col_descs,
                "value_legend": legend,
            }
        )

    logger.info("Dibangun %d dokumen skema dari %s", len(docs), DB_PATH)
    return docs
