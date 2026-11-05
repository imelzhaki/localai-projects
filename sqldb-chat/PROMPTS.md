# Panduan Prompt untuk Operator DBChat (Elektronik Retail)

Dokumen ini berisi daftar prompt yang dapat digunakan operator non-coder untuk mengakses database perusahaan retail elektronik melalui DBChat. Semua prompt dalam Bahasa Indonesia.

## 1. Manajemen Customer (Pelanggan)

| # | Prompt | Alat yang dipanggil | Hasil yang diharapkan |
|---|--------|---------------------|----------------------|
| 1 | "Berapa jumlah customer yang ada?" | `get_database_stats()` | Jumlah total customer (20) |
| 2 | "List semua customer" | `list_customers()` | Daftar 20 customer dengan nama, kota, telepon, email |
| 3 | "Cari customer yang nama-nya Budi" | `get_customer(nama="Budi")` | Customer dengan nama mengandung "Budi" |
| 4 | "Customer yang tinggal di Jakarta" | `get_customer(kota="Jakarta")` | Daftar customer di Kota Jakarta |
| 5 | "Detail customer ID 1" | `get_customer(customer_id=1)` | Detail lengkap customer Budi Santoso |
| 6 | "Customer yang tidak ada di database" | `get_customer(nama="Xyz123")` | "Tidak ada data yang ditemukan." |

## 2. Manajemen Produk

| # | Prompt | Alat yang dipanggil | Hasil yang diharapkan |
|---|--------|---------------------|----------------------|
| 7 | "List semua produk" | `list_products()` | Daftar 30 produk dengan nama, kategori, harga, stok |
| 8 | "Produk kategori Elektronik" | `get_product(kategori="Elektronik")` | Daftar produk kategori Elektronik |
| 9 | "Produk kategori Aksesori" | `get_product(kategori="Aksesori")` | Daftar produk kategori Aksesori |
| 10 | "Produk kategori Komputer" | `get_product(kategori="Komputer")` | Daftar produk kategori Komputer |
| 11 | "Produk dengan stok di bawah 10" | `get_product(stok_max=10)` | Produk dengan stok <= 10 |
| 12 | "Produk dengan harga di bawah 500000" | `get_product(harga_max=500000)` | Produk dengan harga <= 500.000 |
| 13 | "Detail produk Blender" | `get_product(nama="Blender")` | Detail produk Blender |
| 14 | "Detail produk Laptop Asus ROG" | `get_product(nama="Laptop Asus ROG")` | Detail produk Laptop Asus ROG |
| 15 | "Produk yang tidak ada" | `get_product(nama="ProdukXyz")` | "Tidak ada data yang ditemukan." |

## 3. Pesanan Penjualan (Sales Order)

| # | Prompt | Alat yang dipanggil | Hasil yang diharapkan |
|---|--------|---------------------|----------------------|
| 16 | "List semua pesanan penjualan" | `list_sales_orders()` | Daftar 25 pesanan penjualan |
| 17 | "Pesanan penjualan yang sudah lunas" | `get_sales_order(status="Lunas")` | Pesanan dengan status Lunas |
| 18 | "Pesanan penjualan bulan Oktober 2024" | `get_sales_order(rentang_tanggal="2024-10-01 s.d. 2024-10-31")` | Pesanan dalam rentang tanggal |
| 19 | "Detail pesanan penjualan ID 1" | `get_sales_order(order_id=1)` | Detail pesanan ID 1 |
| 20 | "Item dalam pesanan penjualan ID 1" | `get_sales_order_items(order_id=1)` | Detail item produk dalam pesanan ID 1 |
| 21 | "Semua item pesanan penjualan terbaru" | `get_sales_order_items()` | Daftar item pesanan terbaru (limit 50) |

## 4. Pesanan Pembelian (Purchase Order)

| # | Prompt | Alat yang dipanggil | Hasil yang diharapkan |
|---|--------|---------------------|----------------------|
| 22 | "List semua pesanan pembelian" | `list_purchase_orders()` | Daftar 15 pesanan pembelian |
| 23 | "Pesanan pembelian dari supplier ID 1" | `get_purchase_order(supplier_id=1)` | Pesanan pembelian dari supplier ID 1 |
| 24 | "Pesanan pembelian September 2024" | `get_purchase_order(rentang_tanggal="2024-09-01 s.d. 2024-09-30")` | Pesanan pembelian dalam rentang tanggal |

## 5. Supplier

| # | Prompt | Alat yang dipanggil | Hasil yang diharapkan |
|---|--------|---------------------|----------------------|
| 25 | "List semua supplier" | `list_suppliers()` | Daftar 10 supplier |
| 26 | "Detail supplier Toko Elektronik Jaya" | `get_supplier(nama="Toko Elektronik Jaya")` | Detail supplier |
| 27 | "Detail supplier ID 1" | `get_supplier(supplier_id=1)` | Detail supplier ID 1 |

## 6. Analitik Penjualan

| # | Prompt | Alat yang dipanggil | Hasil yang diharapkan |
|---|--------|---------------------|----------------------|
| 28 | "Penjualan kategori Elektronik bulan lalu" | `get_sales_data(category="Elektronik", month="last")` | Penjualan kategori Elektronik bulan terakhir |
| 29 | "Semua penjualan tanpa filter kategori" | `get_sales_data()` | 20 pesanan penjualan terbaru |
| 30 | "Penjualan produk Blender" | `get_sales_by_product(nama_produk="Blender")` | Data penjualan produk Blender |
| 31 | "Penjualan produk Webcam bulan lalu" | `get_sales_by_product(nama_produk="Webcam", month="last")` | Data penjualan Webcam bulan terakhir |
| 32 | "Penjualan produk Laptop" | `get_sales_by_product(nama_produk="Laptop")` | Data penjualan semua produk Laptop |
| 33 | "Tahun berapa saja penjualan dilakukan?" | `get_sales_years()` | Daftar tahun (contoh: ["2024"]) |
| 34 | "Statistik ringkasan database" | `get_database_stats()` | Jumlah baris per tabel |

## 7. Prompt yang Harus Dihindari (akan menyebabkan error/halusinasi)

| # | Prompt yang Salah | Alat yang Salah Dipakai | Alat yang Benar |
|---|-------------------|------------------------|-----------------|
| A | "Penjualan kategori Produk bulan lalu" | `get_sales_data(category="produk")` | `get_sales_data()` (tanpa kategori) atau kategori yang valid: Elektronik, Aksesori, Komputer |
| B | "Penjualan Blender dengan category Elektronik" | `get_sales_by_product(nama_produk="Blender", category="Elektronik")` | `get_sales_by_product(nama_produk="Blender")` (tidak ada parameter category) |
| C | "Penjualan Webcam bulan null" | `get_sales_by_product(nama_produk="Webcam", month="null")` | `get_sales_by_product(nama_produk="Webcam")` (biarkan month kosong) |
| D | "Customer dengan nama *" | `get_customer(nama="*")` | `list_customers()` untuk daftar semua customer |

## Aturan Penting untuk Operator

1. **Selalu verifikasi** jawaban AI terhadap database asli sebelum membuat keputusan bisnis.
2. Jika alat mengembalikan "Tidak ada data yang ditemukan", berarti data benar-benar tidak ada — jangan menebak.
3. Kategori produk yang valid: **Elektronik**, **Aksesori**, **Komputer**.
4. Format rentang tanggal: `"YYYY-MM-DD s.d. YYYY-MM-DD"`.
5. Untuk "bulan lalu", gunakan `month="last"`.
6. Jika tidak yakin parameter apa yang harus dikirim, biarkan kosong dan panggil alat tanpa argumen.