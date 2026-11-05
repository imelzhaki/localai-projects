import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("data/sqldb-chat.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS Customer (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    kota TEXT,
    telepon TEXT,
    email TEXT,
    tanggal_gabung TEXT
);

CREATE TABLE IF NOT EXISTS Supplier (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    kontak TEXT,
    kota TEXT,
    telepon TEXT
);

CREATE TABLE IF NOT EXISTS Product (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    kategori TEXT,
    harga REAL,
    stok INTEGER,
    supplier_id INTEGER,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);

CREATE TABLE IF NOT EXISTS Sales_Order (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    tanggal TEXT,
    total REAL,
    status TEXT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE IF NOT EXISTS Sales_Order_Item (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    kuantitas INTEGER,
    harga_satuan REAL,
    FOREIGN KEY (order_id) REFERENCES Sales_Order(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

CREATE TABLE IF NOT EXISTS Purchase_Order (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER,
    tanggal TEXT,
    total REAL,
    status TEXT,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);
"""

_SAMPLE_DATA = """
INSERT INTO Customer (nama, kota, telepon, email, tanggal_gabung) VALUES
('Budi Santoso', 'Jakarta', '081234567890', 'budi@email.com', '2023-01-15'),
('Siti Rahayu', 'Bandung', '081234567891', 'siti@email.com', '2023-02-20'),
('Ahmad Fauzi', 'Surabaya', '081234567892', 'ahmad@email.com', '2023-03-10'),
('Dewi Lestari', 'Medan', '081234567893', 'dewi@email.com', '2023-04-05'),
('Rudi Hartono', 'Jakarta', '081234567894', 'rudi@email.com', '2023-05-12'),
('Maya Sari', 'Denpasar', '081234567895', 'maya@email.com', '2023-06-18'),
('Joko Widodo', 'Yogyakarta', '081234567896', 'joko@email.com', '2023-07-22'),
('Lina Marlina', 'Makassar', '081234567897', 'lina@email.com', '2023-08-14'),
('Agus Salim', 'Palembang', '081234567898', 'agus@email.com', '2023-09-03'),
('Rina Wulandari', 'Batam', '081234567899', 'rina@email.com', '2023-10-11'),
('Hendra Wijaya', 'Jakarta', '081234567800', 'hendra@email.com', '2023-11-09'),
('Putri Indah', 'Bandung', '081234567801', 'putri@email.com', '2023-12-01'),
('Dedi Kurniawan', 'Surabaya', '081234567802', 'dedi@email.com', '2024-01-17'),
('Sari Dewi', 'Medan', '081234567803', 'sari@email.com', '2024-02-25'),
('Bambang Purwanto', 'Jakarta', '081234567804', 'bambang@email.com', '2024-03-14'),
('Intan Permata', 'Denpasar', '081234567805', 'intan@email.com', '2024-04-20'),
('Tegar Saputra', 'Yogyakarta', '081234567806', 'tegar@email.com', '2024-05-18'),
('Melati Sari', 'Makassar', '081234567807', 'melati@email.com', '2024-06-22'),
('Rizal Ramadhan', 'Palembang', '081234567808', 'rizal@email.com', '2024-07-30'),
('Citra Lestari', 'Batam', '081234567809', 'citra@email.com', '2024-08-15');

INSERT INTO Supplier (nama, kontak, kota, telepon) VALUES
('Toko Elektronik Jaya', 'Andi', 'Jakarta', '021-1234567'),
('Gadget Abadi', 'Budi', 'Bandung', '022-2345678'),
('Komputer Sejahtera', 'Citra', 'Surabaya', '031-3456789'),
('Elektronik Murah', 'Dedi', 'Medan', '061-4567890'),
('Gadget Center', 'Eka', 'Denpasar', '0361-5678901'),
('Komputerindo', 'Fajar', 'Yogyakarta', '0274-6789012'),
('Elektronik Prima', 'Gita', 'Makassar', '0411-7890123'),
('Gadget Store', 'Hadi', 'Palembang', '0711-8901234'),
('Komputer Jaya', 'Ika', 'Batam', '0778-9012345'),
('Elektronik Berkah', 'Joko', 'Jakarta', '021-9012345');

INSERT INTO Product (nama, kategori, harga, stok, supplier_id) VALUES
('Laptop Asus ROG', 'Elektronik', 15000000, 10, 1),
('Smartphone Samsung Galaxy', 'Elektronik', 8000000, 25, 1),
('TV LED 40 Inch', 'Elektronik', 4500000, 15, 1),
('Kulkas 2 Pintu', 'Elektronik', 3500000, 12, 4),
('Mesin Cuci 7kg', 'Elektronik', 3000000, 10, 4),
('Kipas Angin', 'Elektronik', 500000, 30, 4),
('Rice Cooker', 'Elektronik', 300000, 20, 4),
('Setrika Listrik', 'Elektronik', 150000, 25, 4),
('Blender', 'Elektronik', 400000, 18, 4),
('Magicom', 'Elektronik', 350000, 22, 4),
('Mouse Logitech', 'Aksesori', 250000, 40, 2),
('Keyboard Mechanical', 'Aksesori', 600000, 30, 2),
('Headset Gaming', 'Aksesori', 450000, 20, 2),
('Webcam', 'Aksesori', 350000, 15, 2),
('Flashdisk 64GB', 'Aksesori', 150000, 50, 2),
('Kabel USB-C', 'Aksesori', 75000, 60, 2),
('Power Bank 20000mAh', 'Aksesori', 350000, 35, 2),
('Charger Laptop', 'Aksesori', 200000, 28, 2),
('Mousepad Gaming', 'Aksesori', 100000, 45, 2),
('Stabilo Kabel', 'Aksesori', 50000, 70, 2),
('Monitor 24 Inch', 'Komputer', 2500000, 12, 3),
('Keyboard Komputer', 'Komputer', 200000, 35, 3),
('Mouse Komputer', 'Komputer', 150000, 40, 3),
('CPU Intel Core i5', 'Komputer', 4000000, 8, 3),
('RAM 8GB DDR4', 'Komputer', 600000, 25, 3),
('SSD 256GB', 'Komputer', 700000, 20, 3),
('VGA NVIDIA GTX', 'Komputer', 3500000, 5, 3),
('Motherboard ASUS', 'Komputer', 1500000, 10, 3),
('Casing Komputer', 'Komputer', 800000, 12, 3),
('Power Supply 500W', 'Komputer', 500000, 15, 3);

INSERT INTO Sales_Order (customer_id, tanggal, total, status) VALUES
(1, '2024-10-01', 15000000, 'Lunas'),
(2, '2024-10-02', 8000000, 'Lunas'),
(3, '2024-10-03', 4500000, 'Lunas'),
(4, '2024-10-05', 3500000, 'Lunas'),
(5, '2024-10-07', 3000000, 'Lunas'),
(6, '2024-10-08', 500000, 'Lunas'),
(7, '2024-10-10', 300000, 'Lunas'),
(8, '2024-10-12', 150000, 'Lunas'),
(9, '2024-10-14', 400000, 'Lunas'),
(10, '2024-10-15', 350000, 'Lunas'),
(11, '2024-10-17', 250000, 'Lunas'),
(12, '2024-10-18', 600000, 'Lunas'),
(13, '2024-10-20', 450000, 'Lunas'),
(14, '2024-10-21', 350000, 'Lunas'),
(15, '2024-10-23', 150000, 'Lunas'),
(16, '2024-10-24', 75000, 'Lunas'),
(17, '2024-10-26', 350000, 'Lunas'),
(18, '2024-10-27', 200000, 'Lunas'),
(19, '2024-10-28', 100000, 'Lunas'),
(20, '2024-10-30', 2500000, 'Lunas'),
(1, '2024-11-01', 200000, 'Lunas'),
(2, '2024-11-02', 150000, 'Lunas'),
(3, '2024-11-03', 600000, 'Lunas'),
(4, '2024-11-04', 450000, 'Lunas'),
(5, '2024-11-05', 500000, 'Lunas');

INSERT INTO Sales_Order_Item (order_id, product_id, kuantitas, harga_satuan) VALUES
(1, 1, 1, 15000000),
(2, 2, 1, 8000000),
(3, 3, 1, 4500000),
(4, 4, 1, 3500000),
(5, 5, 1, 3000000),
(6, 6, 1, 500000),
(7, 7, 1, 300000),
(8, 8, 1, 150000),
(9, 9, 1, 400000),
(10, 10, 1, 350000),
(11, 11, 1, 250000),
(12, 12, 1, 600000),
(13, 13, 1, 450000),
(14, 14, 1, 350000),
(15, 15, 1, 150000),
(16, 16, 1, 75000),
(17, 17, 1, 350000),
(18, 18, 1, 200000),
(19, 19, 1, 100000),
(20, 20, 1, 2500000),
(21, 1, 1, 15000000),
(22, 2, 1, 8000000),
(23, 13, 1, 600000),
(24, 14, 1, 450000),
(25, 15, 1, 350000),
(26, 16, 1, 500000);

INSERT INTO Purchase_Order (supplier_id, tanggal, total, status) VALUES
(1, '2024-09-01', 50000000, 'Lunas'),
(2, '2024-09-05', 30000000, 'Lunas'),
(3, '2024-09-10', 25000000, 'Lunas'),
(4, '2024-09-12', 20000000, 'Lunas'),
(5, '2024-09-15', 15000000, 'Lunas'),
(6, '2024-09-18', 18000000, 'Lunas'),
(7, '2024-09-20', 22000000, 'Lunas'),
(8, '2024-09-22', 16000000, 'Lunas'),
(9, '2024-09-25', 14000000, 'Lunas'),
(10, '2024-09-28', 12000000, 'Lunas'),
(1, '2024-10-01', 40000000, 'Lunas'),
(2, '2024-10-05', 28000000, 'Lunas'),
(3, '2024-10-10', 26000000, 'Lunas'),
(4, '2024-10-12', 19000000, 'Lunas'),
(5, '2024-10-15', 17000000, 'Lunas');
"""


def get_connection():
    """Buka koneksi SQLite dalam mode read-only (uri mode=ro).

    Mengembalikan objek sqlite3.Connection. Karena dibuka read-only,
    setiap operasi INSERT/UPDATE/DELETE akan ditolak oleh SQLite.
    """
    uri = f"file:{DB_PATH.resolve()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Buat tabel dan seed data sampel jika berkas DB belum ada.

    Jika data/dbchat.db sudah ada, fungsi ini tidak mengubah apa-apa
    (idempotent terhadap data yang sudah ada).
    """
    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        try:
            conn.executescript(_SCHEMA)
            conn.executescript(_SAMPLE_DATA)
            conn.commit()
            logger.info("Database diinisialisasi di %s", DB_PATH)
        finally:
            conn.close()


def execute_query(sql, params=()):
    """Jalankan kueri SELECT parameterisasi dan kembalikan daftar dict.

    Hanya SELECT yang diizinkan. Kueri non-SELECT akan ditolak
    oleh koneksi read-only.
    """
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        rows = [dict(row) for row in cur.fetchall()]
        return rows
    finally:
        conn.close()
