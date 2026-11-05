# Contoh Chat Ollama (Streamlit)

Aplikasi chat web sederhana yang men-streaming respons dari model Ollama `llama3.2:3b`.
Riwayat percakapan diingat dalam sesi dan disimpan ke `data/history.json` sehingga
bertahan setelah aplikasi di-restart.

## Fitur

- Antarmuka web berbasis Streamlit
- Streaming respons token-per-token dari model `llama3.2:3b`
- Riwayat percakapan diingat dalam satu sesi (model melihat pesan sebelumnya)
- Persistensi riwayat ke `data/history.json` (bertahan setelah restart)
- **Membuka dan membaca konten halaman web dari URL yang disertakan user dalam percakapan**
- Penanganan kesalahan jika Ollama tidak terhubung atau model tidak ditemukan

## Prasyarat

- [Ollama](https://ollama.com) terinstal dan berjalan (`ollama serve`)
- Model `llama3.2:3b` telah diunduh (`ollama pull llama3.2:3b`)
- Python 3.10+
- [trafilatura](https://trafilatura.readthedocs.io/) untuk ekstraksi konten artikel dari halaman web (terinstal otomatis via `requirements.txt`)

## Instalasi

```bash
cd C:\Dev\Research\localai-projects\chat-sample
pip install -r requirements.txt
```

## Menjalankan Aplikasi

```bash
streamlit run app.py
```

Buka URL yang dicetak Streamlit (biasanya http://localhost:8501).

## Cara Menggunakan Fitur URL

Tempelkan URL langsung dalam kotak percakapan, misalnya:

```
Baca https://example.com dan ringkas isinya
```

Aplikasi akan:
1. Mendeteksi URL dalam pesan Anda
2. Membuka halaman web dan mengekstrak teksnya
3. Menyisipkan konten halaman sebagai konteks untuk model
4. Menjawab pertanyaan Anda berdasarkan konten halaman tersebut

Jika pengambilan halaman gagal (situs memblokir, tidak dapat diakses, atau bukan HTML), aplikasi akan menampilkan peringatan dan melanjutkan respons tanpa konten web.

Anda dapat menyertakan beberapa URL dalam satu pesan.

## Perintah Khusus

Ketik perintah berikut dalam kotak percakapan:

| Perintah | Fungsi |
|----------|--------|
| `/reset` | Menghapus semua riwayat percakapan dan menggambar konteks |
| `/clear` | Sama dengan `/reset` |
| `/summary` | Membuat ringkasan dari seluruh percakapan yang telah terjadi |

Contoh:
```
/reset
```
Riwayat percakapan akan dihapus sepenuhnya, termasuk file `data/history.json`.

```
/summary
```
Model akan membuat ringkasan ringkas dari semua pesan yang telah dipertukarkan dalam sesi ini.

## Struktur Proyek

```
chat-sample/
├── app.py              # Titik masuk Streamlit: UI, riwayat sesi, streaming, persistensi
├── history.py          # Muat/simpan riwayat chat ke data/history.json
├── ollama_client.py    # Pembungkus streaming ollama.Client.chat(stream=True)
├── web_fetcher.py      # Deteksi URL dan pengambilan konten halaman web
├── requirements.txt    # Dependensi Python (streamlit, ollama)
├── .gitignore          # Abaikan __pycache__, *.pyc, data/
├── README.md           # Dokumentasi ini
└── tests/
    ├── test_app.py           # Tes untuk app.py
    ├── test_history.py       # Tes untuk history.py
    ├── test_ollama_client.py # Tes untuk ollama_client.py
    └── test_web_fetcher.py   # Tes untuk web_fetcher.py
```

## Cara Kerja

1. User mengetik pesan di `st.chat_input` dan tekan Enter
2. Pesan user ditambahkan ke riwayat `session_state` dan ditampilkan
3. **Jika pesan mengandung URL, aplikasi secara otomatis membuka halaman web dan mengekstrak teks artikelnya melalui `web_fetcher.py` (menggunakan [trafilatura](https://trafilatura.readthedocs.io/) untuk membersihkan boilerplate halaman web)**
4. Konten halaman web disisipkan sebagai pesan sistem (konteks) bersama riwayat percakapan
5. Riwayat lengkap (termasuk konten URL) dikirim ke `ollama_client.chat_stream(messages)` yang menghasilkan potongan teks
6. Potongan di-stream ke `st.chat_message("assistant")` melalui `st.write_stream`
7. Respons asisten lengkap disimpan ke riwayat dan ke `data/history.json`
8. Saat aplikasi dimuat ulang, riwayat dipulihkan dari `data/history.json`

## Pengujian

```bash
pytest tests/ -v
```

Harapan: 26 tes lulus (3 history + 2 ollama_client + 9 app + 12 web_fetcher).

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Ollama tidak terhubung | Jalankan `ollama serve` terlebih dahulu |
| Model `llama3.2:3b` tidak ditemukan | Jalankan `ollama pull llama3.2:3b` |
| `streamlit` tidak dikenali | Jalankan `pip install -r requirements.txt` |
| Konten halaman web tidak terbaca | Pastikan URL dapat diakses dan mengembalikan HTML. Beberapa situs (mis. detik.com) memblokir pengambilan otomatis melalui User-Agent atau membatasi akses. Aplikasi akan menampilkan peringatan per URL dengan alasan kesalahan dan melanjutkan respons tanpa konten web. |
| URL tertentu gagal dibuka | Lihat pesan peringatan yang menunjukkan URL mana yang gagal dan alasan kesalahannya (mis. timeout, koneksi ditolak, atau bukan HTML). Coba URL lain atau buka situs tersebut langsung di browser. |
| Beberapa URL, sebagian gagal | Aplikasi menampilkan konten dari URL yang berhasil dan peringatan untuk URL yang gagal. Model akan menjawab berdasarkan konten yang tersedia. |

## Lisensi

MIT
