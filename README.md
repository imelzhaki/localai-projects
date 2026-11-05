# localai-projects

Berbagai project yang menggunakan Local AI (Llama 3.2 3B via Ollama).

## Daftar Project

| Project | Deskripsi | Teknologi |
|---------|-----------|-----------|
| `chat-sample` | Chat sederhana dengan riwayat dan fetch konten web | Streamlit, Ollama, trafilatura |
| `db-chat` | Agent panggilan fungsi untuk database kantor (read-only SQL) | Streamlit, Ollama, SQLite |
| `sqldb-chat` | Chat terhadap database SQL dengan retrieval dan validasi | Streamlit, Ollama, ChromaDB, SQLite |
| `dispatcher-bot` | Bot Telegram yang mengklasifikasikan pesan masuk dan meneruskan notifikasi ke grup departemen | Python, Ollama, requests |

## Project Terbaru: dispatcher-bot

**Lokasi:** `localai-projects/dispatcher-bot/`

Bot Telegram yang menerima pesan masuk, mengklasifikasikannya dengan Llama 3.2 3B (via Ollama, `format: "json"`) menjadi JSON terstruktur (departemen, prioritas, kategori, ringkasan), dan meneruskan notifikasi ke grup Telegram departemen yang terkait (IT_SUPPORT, HR, FINANCE, GENERAL).

### Menjalankan

```bash
cd C:\Dev\Research\localai-projects\dispatcher-bot
pip install -r requirements.txt
```

Konfigurasi variabel lingkungan (`TELEGRAM_BOT_TOKEN`, `*_GROUP_ID`, `OLLAMA_HOST`, `OLLAMA_MODEL`), lalu:

```bash
python app.py
```

### Pengujian

```bash
pytest tests/ -v
```

Hasil: 20 tes lulus.

## Prasyarat Umum

- Ollama terinstal dan berjalan (`ollama serve`)
- Model `llama3.2:3b` diunduh (`ollama pull llama3.2:3b`)
- Python 3.10+