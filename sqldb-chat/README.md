# SQLDB-Chat — Text-to-SQL dengan Pemahaman Skema (Llama 3.2 3B)

SQLDB-Chat adalah aplikasi Text-to-SQL yang menerjemahkan pertanyaan bahasa alami (Bahasa Indonesia atau Inggris) menjadi kueri SQL yang dieksekusi terhadap database SQLite read-only. Didesain khusus untuk model kecil (llama3.2:3b) di mana **pemahaman skema** adalah tantangan terbesar — bukan sintaks SQL.

Alih-alih function calling, SQLDB-Chat menggunakan pipeline **schema comprehension**:

1. **Retrieve skema** — Ambil dokumen skema yang relevan dari indeks ChromaDB (dibangun dari SQLAlchemy Inspector metadata, bukan DDL mentah).
2. **Generate SQL** — llama3.2:3b menghasilkan SQL dengan system prompt bilingual, skema yang diambil, dan contoh few-shot.
3. **Validasi SQLGlot** — Validasi sintaks dan dialek SQLite, enforce SELECT-only.
4. **Critik LLM** — Kedua llama3.2:3b melakukan review semantik SQL terhadap skema (nama tabel, kolom, join).
5. **Eksekusi read-only** — Jalankan SQL terhadap SQLite dalam mode read-only (`mode=ro`).
6. **Render hasil** — Tampilkan SQL dan hasil kueri di Streamlit UI.

## Fitur

- **Schema comprehension pipeline** — Retrieve → Generate → Validate → Critic → Execute, tanpa function calling.
- **Metadata skema, bukan DDL mentah** — Setiap tabel dilengkapi purpose, deskripsi kolom, dan value legend (mis. `kategori: Elektronik/Aksesori/Komputer`, `status: Lunas`).
- **Few-shot bilingual** — 18 contoh Q/SQL dalam Bahasa Indonesia dan Inggris untuk pola domain ERP.
- **SQLGlot validator** — Gate sintaks SQLite sebelum eksekusi, hanya SELECT yang diizinkan.
- **Second-pass critic** — llama3.2:3b meninjau SQL terhadap skema dan memperbaiki kesalahan nama tabel/kolom/join.
- **Read-only by design** — Koneksi SQLite dibuka dalam mode read-only (`mode=ro`).
- **Riwayat percakapan** — Riwayat chat disimpan ke `data/history.json` dan dapat direset dengan perintah `/reset` atau `/clear`.
- **Streamlit UI** — Antarmuka chat sederhana berbasis web dengan ekspander untuk melihat SQL yang dihasilkan.

## Struktur Project

```
sqldb-chat/
├── app.py                 # Streamlit UI (chat, /reset, /clear, SQL expander, dataframe)
├── database.py            # Layer database: read-only SQLite, skema, seed data, init_db
├── schema.py              # SQLAlchemy Inspector → dokumen metadata per tabel (purpose, columns, value_legend)
├── retrieval.py           # sentence-transformers embeddings → ChromaDB → retrieve_schema_docs(question, top_k)
├── fewshot.py             # 18 contoh Q/SQL bilingual (id+en), get_fewshot_examples()
├── validation.py          # SQLGlot dialect gate, validate_sql() enforces SELECT-only
├── critic.py              # Second llama3.2:3b semantic review, critique_sql()
├── execution.py           # Read-only SELECT execution, execute_select() dengan mode=ro
├── ollama_client.py       # generate_sql(question, schema_docs, fewshot_examples) — ganti chat_with_tools
├── history.py             # load_history / save_history ke data/history.json
├── tools.py               # (legacy) 15 fungsi read-only dari db-chat, tidak lagi digunakan oleh app.py
├── requirements.txt       # Dependensi Python
├── .gitignore             # Git ignore
├── README.md              # Dokumentasi ini
├── PROMPTS.md             # Panduan prompt untuk operator (Text-to-SQL)
├── data/
│   ├── sqldb-chat.db      # Database SQLite (dihasilkan oleh init_db)
│   ├── history.json       # Riwayat percakapan (dihasilkan oleh aplikasi)
│   └── chroma_db/         # Indeks ChromaDB untuk retrieval skema
└── tests/
    ├── test_schema.py     # 3 TDD tests (schema layer)
    ├── test_retrieval.py  # 2 TDD tests (retrieval layer)
    ├── test_fewshot.py    # 4 TDD tests (few-shot layer)
    ├── test_validation.py # 6 TDD tests (validation layer)
    ├── test_execution.py  # 4 TDD tests (execution layer)
    ├── test_critic.py     # 3 TDD tests (critic layer)
    ├── test_ollama_client.py  # 2 TDD tests (ollama client)
    ├── test_app.py        # 2 TDD tests (Streamlit app process_question)
    ├── test_database.py   # 6 TDD tests (database layer)
    ├── test_tools.py      # 22 TDD tests (legacy tools layer)
    ├── test_history.py    # 3 TDD tests (history layer)
    └── test_operator_prompts.py  # 38 TDD tests (operator prompts)
```

Total: 102 tes, semuanya lolos.

## Persyaratan

- Python 3.10+
- Ollama terinstal dan berjalan (model `llama3.2:3b` di-pull)
- Streamlit, ollama (Python client), sqlalchemy, sqlglot, chromadb, sentence-transformers

## Instalasi

```bash
# Masuk ke direktori project
cd C:\Dev\Research\localai-projects\sqldb-chat

# Install dependensi
pip install -r requirements.txt

# Pull model Llama 3.2 ke Ollama
ollama pull llama3.2:3b

# Jalankan aplikasi
streamlit run app.py
```

## Contoh Penggunaan

Ketik pertanyaan dalam Bahasa Indonesia atau Inggris di kotak chat. Setiap permintaan diproses melalui pipeline schema comprehension:

| Pertanyaan | SQL yang dihasilkan |
|------------|---------------------|
| "Tampilkan pelanggan di Jakarta." | `SELECT * FROM Customer WHERE kota = 'Jakarta';` |
| "Show all customers." | `SELECT * FROM Customer;` |
| "Berapa jumlah pelanggan?" | `SELECT COUNT(*) AS jumlah_pelanggan FROM Customer;` |
| "Tampilkan produk kategori Elektronik." | `SELECT * FROM Product WHERE kategori = 'Elektronik';` |
| "Tampilkan pesanan penjualan untuk Budi Santoso." | `SELECT so.* FROM Sales_Order so JOIN Customer c ON so.customer_id = c.customer_id WHERE c.nama = 'Budi Santoso';` |
| "/reset" atau "/clear" | Hapus riwayat percakapan |

Lihat daftar lengkap prompt di `PROMPTS.md`.

## Arsitektur

1. **app.py** — Streamlit terima input user, menjalankan `process_question()` (pipeline lengkap), menampilkan SQL dan hasil kueri.
2. **schema.py** — `build_schema_docs()` introspeksi SQLite via SQLAlchemy Inspector, membuat dokumen metadata per tabel (bukan DDL mentah).
3. **retrieval.py** — `build_index()` dan `retrieve_schema_docs()` menggunakan sentence-transformers + ChromaDB untuk pencarian skema yang relevan.
4. **fewshot.py** — `get_fewshot_examples()` menyediakan 18 contoh Q/SQL bilingual untuk few-shot prompting.
5. **ollama_client.py** — `generate_sql()` membangun prompt bilingual dengan skema + few-shot, memanggil llama3.2:3b (temperature 0.1), mengekstrak SQL.
6. **validation.py** — `validate_sql()` menggunakan SQLGlot (dialek SQLite) untuk validasi sintaks, enforce SELECT-only.
7. **critic.py** — `critique_sql()` memanggil llama3.2:3b untuk review semantik SQL terhadap skema yang diambil.
8. **execution.py** — `execute_select()` menjalankan SQL SELECT terhadap SQLite dalam mode read-only.
9. **database.py** — Koneksi SQLite read-only, inisialisasi skema dan data sampel.
10. **history.py** — Simpan/muat riwayat chat ke `data/history.json`.

## Panduan Prompt untuk Operator

Lihat `PROMPTS.md` untuk panduan prompt Text-to-SQL.

## Lisensi

Internal use — database kantor.
