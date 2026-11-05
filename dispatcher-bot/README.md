# Dispatcher Bot

Bot Telegram yang menerima pesan masuk, mengklasifikasikannya dengan Llama 3.2 3B
(via Ollama) menjadi JSON terstruktur (departemen, prioritas, kategori, ringkasan),
dan meneruskan notifikasi ke grup Telegram departemen yang terkait.

## Prasyarat

- Ollama terinstal dan berjalan (`ollama serve`)
- Model `llama3.2:3b` diunduh (`ollama pull llama3.2:3b`)
- Python 3.10+
- Token bot Telegram (dari @BotFather)
- Chat ID grup per departemen

## Instalasi

```bash
cd C:\Dev\Research\localai-projects\dispatcher-bot
pip install -r requirements.txt
```

## Konfigurasi

Buat berkas `.env` atau set variabel lingkungan:

```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
export IT_SUPPORT_GROUP_ID="-1001234567890"
export HR_GROUP_ID="-1001234567891"
export FINANCE_GROUP_ID="-1001234567892"
export GENERAL_GROUP_ID="-1001234567893"
export ADMIN_GROUP_ID="-1001234567899"
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODEL="llama3.2:3b"
```

## Menjalankan

```bash
python app.py
```

Bot akan polling pesan dari Telegram. Setiap pesan baru diklasifikasikan dan
notifikasi dikirim ke grup departemen yang sesuai. Riwayat disimpan di
`data/history.json`.

## Pengujian

```bash
pytest tests/ -v
```

## Skema Output JSON

```json
{
  "department": "IT_SUPPORT | HR | FINANCE | GENERAL",
  "priority": "LOW | MEDIUM | HIGH | URGENT",
  "category": "HARDWARE_FAILURE | SOFTWARE_ISSUE | NETWORK | LEAVE_REQUEST | PAYROLL | ONBOARDING | INVOICE | REIMBURSEMENT | BUDGET | INQUIRY | FEEDBACK",
  "summary": "string"
}
```