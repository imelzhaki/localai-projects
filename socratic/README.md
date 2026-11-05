# Socratic Tutor Bot

Aplikasi chat web Streamlit yang bertindak sebagai tutor bimbingan belajar interaktif menggunakan metode Socratic. Model `llama3.2:3b` melalui Ollama hanya mengajukan pertanyaan penuntang — tidak memberikan rumus atau jawaban langsung.

Tahap bimbingan:
- **Guiding**: hanya pertanyaan penuntang (default 3 pertanyaan)
- **Hint**: petunjuk kecil diizinkan setelah 3 pertanyaan
- **Reveal**: jawaban lengkap + penjelasan singkat setelah lebih lanjut

Riwayat percakapan disimpan ke `data/history.json` dan bertahan setelah restart. Terdapat tombol "Mulai topik baru" dan perintah `/reset` untuk memulai topik baru.

## Prasyarat

- Ollama berjalan (`ollama serve`)
- Model `llama3.2:3b` diunduh (`ollama pull llama3.2:3b`)
- Python 3.10+

## Jalankan

```bash
cd C:\Dev\Research\localai-projects\socratic
pip install -r requirements.txt
streamlit run app.py
```

Buka URL yang dicetak Streamlit (biasanya http://localhost:8501).
