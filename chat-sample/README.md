# Contoh Chat Ollama

Aplikasi chat Streamlit sederhana yang men-streaming respons dari Ollama `llama3.2:3b`.
Riwayat percakapan diingat dalam sesi dan disimpan ke
`data/history.json` sehingga bertahan setelah aplikasi di-restart.

## Prasyarat

- Ollama berjalan (`ollama serve`)
- Model `llama3.2:3b` diunduh (`ollama pull llama3.2:3b`)

## Jalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Buka URL yang dicetak Streamlit (biasanya http://localhost:8501).
