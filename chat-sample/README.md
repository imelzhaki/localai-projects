# Contoh Chat Ollama (Streamlit)

Aplikasi chat web sederhana yang men-streaming respons dari model Ollama `llama3.2:3b`.
Riwayat percakapan diingat dalam sesi dan disimpan ke `data/history.json` sehingga
bertahan setelah aplikasi di-restart.

## Fitur

- Antarmuka web berbasis Streamlit
- Streaming respons token-per-token dari model `llama3.2:3b`
- Riwayat percakapan diingat dalam satu sesi (model melihat pesan sebelumnya)
- Persistensi riwayat ke `data/history.json` (bertahan setelah restart)
- Penanganan kesalahan jika Ollama tidak terhubung atau model tidak ditemukan

## Prasyarat

- [Ollama](https://ollama.com) terinstal dan berjalan (`ollama serve`)
- Model `llama3.2:3b` telah diunduh (`ollama pull llama3.2:3b`)
- Python 3.10+

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

## Struktur Proyek

```
chat-sample/
├── app.py              # Titik masuk Streamlit: UI, riwayat sesi, streaming, persistensi
├── history.py          # Muat/simpan riwayat chat ke data/history.json
├── ollama_client.py    # Pembungkus streaming ollama.Client.chat(stream=True)
├── requirements.txt    # Dependensi Python (streamlit, ollama)
├── .gitignore          # Abaikan __pycache__, *.pyc, data/
├── README.md           # Dokumentasi ini
└── tests/
    ├── test_app.py           # Tes untuk app.py
    ├── test_history.py       # Tes untuk history.py
    └── test_ollama_client.py # Tes untuk ollama_client.py
```

## Cara Kerja

1. User mengetik pesan di `st.chat_input` dan tekan Enter
2. Pesan user ditambahkan ke riwayat `session_state` dan ditampilkan
3. Riwayat lengkap dikirim ke `ollama_client.chat_stream(messages)` yang menghasilkan potongan teks
4. Potongan di-stream ke `st.chat_message("assistant")` melalui `st.write_stream`
5. Respons asisten lengkap disimpan ke riwayat dan ke `data/history.json`
6. Saat aplikasi dimuat ulang, riwayat dipulihkan dari `data/history.json`

## Pengujian

```bash
pytest tests/ -v
```

Harapan: 7 tes lulus (3 history + 2 ollama_client + 2 app).

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Ollama tidak terhubung | Jalankan `ollama serve` terlebih dahulu |
| Model `llama3.2:3b` tidak ditemukan | Jalankan `ollama pull llama3.2:3b` |
| `streamlit` tidak dikenali | Jalankan `pip install -r requirements.txt` |

## Lisensi

MIT
