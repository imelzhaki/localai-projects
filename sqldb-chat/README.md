# DBChat — Agent Database Kantor (Llama 3.2 3B)

DBChat adalah jembatan antara pengguna non-coder dan database internal kantor. Model (Llama 3.2 3B melalui Ollama) bertindak sebagai penerjemah perintah harian dalam Bahasa Indonesia menjadi **panggilan fungsi (function call)** yang dieksekusi terhadap database SQLite read-only.

Setiap jawaban dihasilkan **melalui teknik function call** — model tidak menebak atau mengarang data, melainkan memanggil alat (tool) yang mengakses database secara langsung. Hasil alat kemudian dikembalikan ke model untuk disajikan kepada user. Ini memastikan data keuangan dan bisnis akurat dan terverifikasi.

## Fitur

- **Natural language to function call** — Ketik perintah dalam Bahasa Indonesia, model menerjemahkannya menjadi panggilan fungsi (tool call) yang dieksekusi terhadap database.
- **Native tool calling** — Menggunakan Ollama native tool calling yang stabil untuk otomatisasi perangkat lunak.
- **Read-only by design** — Koneksi SQLite dibuka dalam mode read-only (`mode=ro`), sehingga database tidak dapat dimodifikasi melalui aplikasi.
- **Riwayat percakapan** — Riwayat chat disimpan ke `data/history.json` dan dapat direset dengan perintah `/reset` atau `/clear`.
- **Streamlit UI** — Antarmuka chat sederhana berbasis web.
- **Anti-halucinasi** — System prompt dengan aturan ketat: jawab hanya berdasarkan hasil alat, jangan mengarang data, verifikasi terhadap database asli sebelum keputusan bisnis.

## Struktur Project

```
db-chat/
├── app.py                 # Streamlit UI (chat, /reset, /clear, tool result display)
├── database.py            # Layer database: read-only SQLite, skema, seed data, execute_query
├── tools.py               # 15 fungsi read-only + skema alat Ollama + execute_tool_map
├── ollama_client.py       # chat_with_tools() (loop round-trip function calling) + execute_tool()
├── history.py             # load_history / save_history ke data/history.json
├── requirements.txt       # Dependensi Python
├── .gitignore             # Git ignore
├── README.md              # Dokumentasi ini
├── PROMPTS.md             # Panduan prompt untuk operator (34+ prompt)
├── data/
│   ├── dbchat.db          # Database SQLite (dihasilkan oleh init_db)
│   └── history.json       # Riwayat percakapan (dihasilkan oleh aplikasi)
└── tests/
    ├── test_database.py   # 6 TDD tests (database layer)
    ├── test_tools.py      # 22 TDD tests (tools layer)
    ├── test_ollama_client.py  # 2 TDD tests (ollama client)
    ├── test_history.py    # 3 TDD tests (history layer)
    ├── test_app.py        # 4 TDD tests (Streamlit app)
    └── test_operator_prompts.py  # 38 TDD tests (operator prompts)
```

Total: 82 tes, semuanya lolos.

## Persyaratan

- Python 3.10+
- Ollama terinstal dan berjalan (model `llama3.2:3b` di-pull, disarankan `llama3.2:7b` atau lebih besar untuk function call yang lebih andal pada data keuangan)
- Streamlit, ollama (Python client)

## Instalasi

```bash
# Masuk ke direktori project
cd C:\Dev\Research\localai-projects\db-chat

# Install dependensi
pip install -r requirements.txt

# Pull model Llama 3.2 ke Ollama
ollama pull llama3.2:3b

# Jalankan aplikasi
streamlit run app.py
```

## Contoh Penggunaan

Ketik perintah dalam Bahasa Indonesia di kotak chat. Setiap permintaan diproses **melalui teknik function call**:

| Perintah | Fungsi yang dipanggil |
|----------|----------------------|
| "Tolong carikan data penjualan produk kategori Elektronik bulan lalu." | `get_sales_data(category="Elektronik", month="last")` |
| "Tampilkan data customer dengan ID 5." | `get_customer(customer_id=5)` |
| "Berapa jumlah customer yang ada?" | `get_database_stats()` |
| "List semua produk kategori Elektronik" | `list_products(kategori="Elektronik")` |
| "Produk dengan stok di bawah 10" | `list_products(stok_max=10)` |
| "Detail produk Laptop Asus ROG" | `get_product(nama="Laptop Asus ROG")` |
| "Pesanan penjualan yang sudah lunas" | `get_sales_order(status="Lunas")` |
| "Tampilkan daftar supplier." | `list_suppliers()` |
| "Statistik ringkasan database" | `get_database_stats()` |
| "/reset" atau "/clear" | Hapus riwayat percakapan |

Lihat daftar lengkap prompt di `PROMPTS.md`.

## Arsitektur

1. **app.py** — Streamlit terima input user, memanggil `chat_with_tools`, menampilkan hasil dan panggilan fungsi.
2. **ollama_client.py** — `chat_with_tools()` mengirim pesan ke Ollama dengan skema fungsi. Jika model meminta function call, dieksekusi melalui `execute_tool()` dan hasilnya dikembalikan ke model untuk jawaban akhir.
3. **tools.py** — 15 fungsi read-only + `execute_tool_map` untuk dispatch function call ke fungsi yang sesuai.
4. **database.py** — Koneksi SQLite read-only, inisialisasi skema dan data sampel, `execute_query` yang menolak query non-SELECT.
5. **history.py** — Simpan/muat riwayat chat ke `data/history.json`.

## Alat yang Tersedia (15 fungsi)

| Fungsi | Deskripsi |
|--------|-----------|
| `get_sales_data(category, month)` | Data penjualan per kategori dan bulan. |
| `get_customer(customer_id, nama, kota)` | Detail customer berdasarkan ID, nama, atau kota. |
| `get_product(product_id, nama, kategori, stok_max, harga_max)` | Detail produk dengan filter ID, nama, kategori, stok, atau harga. |
| `get_sales_order(order_id, customer_id, rentang_tanggal, status)` | Pesanan penjualan dengan filter ID, pelanggan, tanggal, atau status. |
| `get_purchase_order(order_id, supplier_id, rentang_tanggal)` | Pesanan pembelian dengan filter ID, supplier, atau tanggal. |
| `get_supplier(supplier_id, nama)` | Detail supplier berdasarkan ID atau nama. |
| `list_customers()` | Daftar semua customer. |
| `list_sales_orders()` | Daftar semua pesanan penjualan. |
| `list_purchase_orders()` | Daftar semua pesanan pembelian. |
| `list_suppliers()` | Daftar semua supplier. |
| `list_products(kategori, stok_max, harga_max)` | Daftar semua produk dengan opsi filter kategori, stok, atau harga. |
| `get_sales_order_items(order_id)` | Detail item dalam pesanan penjualan. |
| `get_sales_by_product(nama_produk, month)` | Data penjualan untuk produk tertentu. |
| `get_database_stats()` | Statistik ringkasan: jumlah baris per tabel. |
| `get_sales_years()` | Daftar tahun yang terdapat data penjualan. |

## Panduan Prompt untuk Operator

Lihat `PROMPTS.md` untuk 34+ prompt contoh yang terorganisir menurut domain bisnis (Customer, Produk, Pesanan Penjualan, Pesanan Pembelian, Supplier, Analitik Penjualan), beserta prompt yang harus dihindari.

## Lisensi

Internal use — database kantor.
