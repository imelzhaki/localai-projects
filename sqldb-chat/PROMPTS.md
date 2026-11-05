# Panduan Prompt untuk Operator SQLDB-Chat (Elektronik Retail)

Dokumen ini berisi daftar pertanyaan (prompt) yang dapat digunakan operator non-coder untuk mengakses database perusahaan retail elektronik melalui SQLDB-Chat. Semua prompt dalam Bahasa Indonesia atau Inggris.

SQLDB-Chat menggunakan pendekatan **Text-to-SQL dengan pemahaman skema**: model menerima pertanyaan bahasa alami, menghasilkan kueri SQL, memvalidasinya, dan mengeksekusinya terhadap database SQLite read-only. Tidak ada function calling — hanya generate SQL → validasi → eksekusi.

## 1. Manajemen Customer (Pelanggan)

| # | Pertanyaan | SQL yang dihasilkan | Hasil yang diharapkan |
|---|-----------|---------------------|----------------------|
| 1 | "Berapa jumlah customer yang ada?" | `SELECT COUNT(*) AS jumlah_pelanggan FROM Customer;` | Jumlah total customer (20) |
| 2 | "List semua customer" | `SELECT * FROM Customer;` | Daftar 20 customer dengan nama, kota, telepon, email |
| 3 | "Cari customer yang nama-nya Budi" | `SELECT * FROM Customer WHERE nama LIKE '%Budi%';` | Customer dengan nama mengandung "Budi" |
| 4 | "Customer yang tinggal di Jakarta" | `SELECT * FROM Customer WHERE kota = 'Jakarta';` | Daftar customer di Kota Jakarta |
| 5 | "Detail customer ID 1" | `SELECT * FROM Customer WHERE customer_id = 1;` | Detail lengkap customer Budi Santoso |
| 6 | "Customer yang tidak ada di database" | `SELECT * FROM Customer WHERE nama = 'Xyz123';` | "Tidak ada data yang ditemukan." |

## 2. Manajemen Produk

| # | Pertanyaan | SQL yang dihasilkan | Hasil yang diharapkan |
|---|-----------|---------------------|----------------------|
| 7 | "List semua produk" | `SELECT * FROM Product;` | Daftar 30 produk dengan nama, kategori, harga, stok |
| 8 | "Produk kategori Elektronik" | `SELECT * FROM Product WHERE kategori = 'Elektronik';` | Daftar produk kategori Elektronik |
| 9 | "Produk kategori Aksesori" | `SELECT * FROM Product WHERE kategori = 'Aksesori';` | Daftar produk kategori Aksesori |
| 10 | "Produk kategori Komputer" | `SELECT * FROM Product WHERE kategori = 'Komputer';` | Daftar produk kategori Komputer |
| 11 | "Produk dengan stok di bawah 10" | `SELECT * FROM Product WHERE stok < 10;` | Produk dengan stok < 10 |
| 12 | "Produk dengan harga di bawah 500000" | `SELECT * FROM Product WHERE harga < 500000;` | Produk dengan harga < 500.000 |
| 13 | "Detail produk Blender" | `SELECT * FROM Product WHERE nama = 'Blender';` | Detail produk Blender |
| 14 | "Detail produk Laptop Asus ROG" | `SELECT * FROM Product WHERE nama = 'Laptop Asus ROG';` | Detail produk Laptop Asus ROG |
| 15 | "Produk yang tidak ada" | `SELECT * FROM Product WHERE nama = 'ProdukXyz';` | "Tidak ada data yang ditemukan." |

## 3. Pesanan Penjualan (Sales Order)

| # | Pertanyaan | SQL yang dihasilkan | Hasil yang diharapkan |
|---|-----------|---------------------|----------------------|
| 16 | "List semua pesanan penjualan" | `SELECT * FROM Sales_Order;` | Daftar 25 pesanan penjualan |
| 17 | "Pesanan penjualan yang sudah lunas" | `SELECT * FROM Sales_Order WHERE status = 'Lunas';` | Pesanan dengan status Lunas |
| 18 | "Pesanan penjualan bulan Oktober 2024" | `SELECT * FROM Sales_Order WHERE tanggal BETWEEN '2024-10-01' AND '2024-10-31';` | Pesanan dalam rentang tanggal |
| 19 | "Detail pesanan penjualan ID 1" | `SELECT * FROM Sales_Order WHERE order_id = 1;` | Detail pesanan ID 1 |
| 20 | "Item dalam pesanan penjualan ID 1" | `SELECT soi.*, p.nama AS nama_produk FROM Sales_Order_Item soi JOIN Product p ON soi.product_id = p.product_id WHERE soi.order_id = 1;` | Detail item produk dalam pesanan ID 1 |
| 21 | "Total penjualan per pelanggan" | `SELECT c.nama, SUM(so.total) AS total_penjualan FROM Sales_Order so JOIN Customer c ON so.customer_id = c.customer_id GROUP BY c.customer_id, c.nama;` | Total penjualan grouped by customer |

## 4. Pesanan Pembelian (Purchase Order)

| # | Pertanyaan | SQL yang dihasilkan | Hasil yang diharapkan |
|---|-----------|---------------------|----------------------|
| 22 | "List semua pesanan pembelian" | `SELECT * FROM Purchase_Order;` | Daftar 15 pesanan pembelian |
| 23 | "Pesanan pembelian dari supplier ID 1" | `SELECT * FROM Purchase_Order WHERE supplier_id = 1;` | Pesanan pembelian dari supplier ID 1 |
| 24 | "Pesanan pembelian September 2024" | `SELECT * FROM Purchase_Order WHERE tanggal BETWEEN '2024-09-01' AND '2024-09-30';` | Pesanan pembelian dalam rentang tanggal |

## 5. Supplier

| # | Pertanyaan | SQL yang dihasilkan | Hasil yang diharapkan |
|---|-----------|---------------------|----------------------|
| 25 | "List semua supplier" | `SELECT * FROM Supplier;` | Daftar 10 supplier |
| 26 | "Detail supplier Toko Elektronik Jaya" | `SELECT * FROM Supplier WHERE nama = 'Toko Elektronik Jaya';` | Detail supplier |
| 27 | "Detail supplier ID 1" | `SELECT * FROM Supplier WHERE supplier_id = 1;` | Detail supplier ID 1 |

## 6. Analitik Penjualan

| # | Pertanyaan | SQL yang dihasilkan | Hasil yang diharapkan |
|---|-----------|---------------------|----------------------|
| 28 | "Penjualan kategori Elektronik" | `SELECT p.nama, SUM(soi.kuantitas * soi.harga_satuan) AS total FROM Product p JOIN Sales_Order_Item soi ON p.product_id = soi.product_id WHERE p.kategori = 'Elektronik' GROUP BY p.product_id, p.nama;` | Penjualan per produk kategori Elektronik |
| 29 | "Semua penjualan tanpa filter" | `SELECT * FROM Sales_Order;` | 25 pesanan penjualan |
| 30 | "Penjualan produk Blender" | `SELECT p.nama, SUM(soi.kuantitas * soi.harga_satuan) AS total FROM Product p JOIN Sales_Order_Item soi ON p.product_id = soi.product_id WHERE p.nama = 'Blender' GROUP BY p.product_id, p.nama;` | Data penjualan produk Blender |
| 31 | "Statistik ringkasan database" | `SELECT name FROM sqlite_master WHERE type='table';` | Daftar semua tabel dalam database |

## 7. Contoh Pertanyaan dalam Bahasa Inggris

| # | Question | SQL yang dihasilkan |
|---|----------|---------------------|
| E1 | "Show all customers." | `SELECT * FROM Customer;` |
| E2 | "Show customers in Jakarta." | `SELECT * FROM Customer WHERE kota = 'Jakarta';` |
| E3 | "Count all customers." | `SELECT COUNT(*) AS jumlah_pelanggan FROM Customer;` |
| E4 | "Show products in the Elektronik category." | `SELECT * FROM Product WHERE kategori = 'Elektronik';` |
| E5 | "Show products with stock below 20." | `SELECT * FROM Product WHERE stok < 20;` |
| E6 | "Show sales orders for customer Budi Santoso." | `SELECT so.* FROM Sales_Order so JOIN Customer c ON so.customer_id = c.customer_id WHERE c.nama = 'Budi Santoso';` |
| E7 | "Show total sales per customer." | `SELECT c.nama, SUM(so.total) AS total_penjualan FROM Sales_Order so JOIN Customer c ON so.customer_id = c.customer_id GROUP BY c.customer_id, c.nama;` |
| E8 | "Show all purchase orders with status Lunas." | `SELECT * FROM Purchase_Order WHERE status = 'Lunas';` |

## 8. Value Legend (Nilai yang Valid)

| Kolom | Nilai yang Valid | Keterangan |
|-------|-----------------|------------|
| `Product.kategori` | Elektronik, Aksesori, Komputer | Kategori produk |
| `Sales_Order.status` | Lunas | Status transaksi (sudah dibayar) |
| `Purchase_Order.status` | Lunas | Status transaksi (sudah dibayar) |
| `Customer.kota` | Jakarta, Bandung, Surabaya, Medan, Denpasar, Yogyakarta, Makassar, Palembang, Batam | Kota pelanggan |

## 9. Aturan Penting untuk Operator

1. **Selalu verifikasi** jawaban AI terhadap database asli sebelum membuat keputusan bisnis.
2. Jika kueri mengembalikan "Tidak ada data yang ditemukan", berarti data benar-benar tidak ada — jangan menebak.
3. Kategori produk yang valid: **Elektronik**, **Aksesori**, **Komputer**.
4. Status transaksi yang valid: **Lunas**.
5. Format tanggal: `'YYYY-MM-DD'`.
6. SQLDB-Chat hanya mendukung kueri **SELECT** (read-only). INSERT, UPDATE, DELETE, DROP tidak diizinkan.
7. Jika hasil tidak sesuai harapan, coba reformulasi pertanyaan dengan lebih spesifik (sebutkan nama tabel atau kolom yang relevan).
8. Perintah `/reset` atau `/clear` untuk menghapus riwayat percakapan.