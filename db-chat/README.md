# DBChat — Agent Database Kantor (Llama 3.2 3B)

DBChat adalah jembatan antara pengguna non-coder dan database internal kantor. Model (Llama 3.2 3B melalui Ollama) bertindak sebagai penerjemah perintah harian dalam Bahasa Indonesia menjadi fungsi API / aksi sistem yang dieksekusi terhadap database SQLite read-only.

## Fitur

- **Natural language to SQL** — Ketik perintah dalam Bahasa Indonesia, model menerjemahkannya menjadi panggilan alat (tool call) yang dieksekusi terhadap database.
- **Native tool calling** — Menggunakan Ollama native tool calling yang stabil untuk otomatisasi perangkat lunak.
- **Read-only by design** — Koneksi SQLite dibuka dalam mode read-only (`mode=ro`), sehingga database tidak dapat dimodifikasi melalui aplikasi.
- **Riwayat percakapan** — Riwayat chat disimpan ke `data/history.json` dan dapat direset dengan perintah `/reset` atau `/clear`.
- **Streamlit UI** — Antarmuka chat sederhana berbasis web.

## Struktur Project

```
db-chat/
├── app.py                 # Streamlit UI (chat, /reset, /clear, tool result display)
├── database.py            # Layer database: read-only SQLite, skema, seed data, execute_query
├── tools.py               # 6 fungsi read-only + skema alat Ollama + execute_tool_map
├── ollama_client.py       # chat_with_tools() (loop round-trip tool calling) + execute_tool()
├── history.py             # load_history / save_history ke data/history.json
├── requirements.txt       # Dependensi Python
├── .gitignore             # Git ignore
├── README.md              # Dokumentasi ini
├── data/
│   ├── dbchat.db          # Database SQLite (dihasilkan oleh init_db)
│   └── history.json       # Riwayat percakapan (dihasilkan oleh aplikasi)
└── tests/
    ├── test_database.py   # 6 TDD tests (database layer)
    ├── test_tools.py      # 7 TDD tests (tools layer)
    ├── test_ollama_client.py  # 2 TDD tests (ollama client)
    ├── test_history.py    # 3 TDD tests (history layer)
    └── test_app.py        # 4 TDD tests (Streamlit app)
```

Total: 22 tes, semuanya lolos.

## Persyaratan

- Python 3.10+
- Ollama terinstal dan berjalan (model `llama3.2:3b` di-pull)
- Streamlit, ollama (Python client)

## Instalasi

```bash
# Masuk ke direktori project
cd C:\Dev\Research\localai-projects\db-chat

# Install dependensi
pip install -r requirements.txt

# Pull model Llama 3.2 3B ke Ollama
ollama pull llama3.2:3b

# Jalankan aplikasi
streamlit run app.py
```

## Contoh Penggunaan

Ketik perintah dalam Bahasa Indonesia di kotak chat:

| Perintah | Deskripsi |
|----------|-----------|
| "Tolong carikan data penjualan produk kategori Elektronik bulan lalu." | Ambil data penjualan kategori Elektronik |
| "Tampilkan data customer dengan ID 5." | Lihat detail customer |
| "Berapa total penjualan bulan ini?" | Ringkasan penjualan |
| "Tampilkan daftar supplier." | Lihat semua supplier |
| "/reset" atau "/clear" | Hapus riwayat percakapan |

## Arsitektur

1. **app.py** — Streamlit terima input user, memanggil `chat_with_tools`, menampilkan hasil dan panggilan alat.
2. **ollama_client.py** — `chat_with_tools()` mengirim pesan ke Ollama dengan skema alat. Jika model meminta tool call, dieksekusi dan hasilnya dikembalikan ke model untuk jawaban akhir.
3. **tools.py** — 6 fungsi read-only (`get_sales_data`, `get_customer`, `get_product`, `get_sales_order`, `get_purchase_order`, `get_supplier`) + `execute_tool_map` untuk dispatch.
4. **database.py** — Koneksi SQLite read-only, inisialisasi skema dan data sampel, `execute_query` yang menolak query non-SELECT.
5. **history.py** — Simpan/muat riwayat chat ke `data/history.json`.

## Alat yang Tersedia

- `get_sales_data(category, month)` — Data penjualan berdasarkan kategori dan bulan.
- `get_customer(customer_id)` — Detail customer berdasarkan ID.
- `get_product(category)` — Daftar produk berdasarkan kategori.
- `get_sales_order(order_id)` — Detail pesanan penjualan.
- `get_purchase_order(order_id)` — Detail pesanan pembelian.
- `get_supplier(supplier_id)` — Detail supplier.

## Lisensi

Internal use — database kantor.
